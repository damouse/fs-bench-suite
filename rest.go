package main

import (
	"bytes"
	"fmt"
	"math/rand"
	"net"
	"net/http"
	"os"
	"strconv"
	"time"

	"./shared"
	"github.com/ant0ine/go-json-rest/rest"
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

type Reminder struct {
	Id        int64     `json:"id"`
	Message   string    `sql:"size:1024" json:"message"`
	CreatedAt time.Time `json:"createdAt"`
	UpdatedAt time.Time `json:"updatedAt"`
}

type Impl struct {
	DB *gorm.DB
}

func StartServer() net.Listener {

	i := Impl{}
	var err error
	i.DB, err = gorm.Open("postgres", "host=localhost user=postgres dbname=mydb sslmode=disable password=postgres")
	shared.CheckErr(err)

	i.DB.Delete(Reminder{})
	i.DB.LogMode(false)
	i.DB.AutoMigrate(&Reminder{})

	api := rest.NewApi()
	api.Use(&rest.TimerMiddleware{},
		&rest.RecorderMiddleware{},
		&rest.PoweredByMiddleware{},
		&rest.RecoverMiddleware{})

	router, err := rest.MakeRouter(
		rest.Post("/reminders", i.PostReminder),
		rest.Get("/reminders/:id", i.GetReminder),
	)

	shared.CheckErr(err)
	api.SetApp(router)

	l, err := net.Listen("tcp", ":8080")
	shared.CheckErr(err)

	go func() {
		http.Serve(l, api.MakeHandler())
	}()

	return l
}

func (i *Impl) GetReminder(w rest.ResponseWriter, r *rest.Request) {
	id := r.PathParam("id")
	reminder := Reminder{}

	if i.DB.First(&reminder, id).Error != nil {
		rest.NotFound(w, r)
		return
	}

	w.WriteJson(&reminder)
}

func (i *Impl) PostReminder(w rest.ResponseWriter, r *rest.Request) {
	reminder := Reminder{}

	if err := r.DecodeJsonPayload(&reminder); err != nil {
		rest.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if err := i.DB.Save(&reminder).Error; err != nil {
		rest.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteJson(&reminder)
}

func Query() *shared.Result {
	var req *http.Response
	var err error

	res := &shared.Result{
		Start: shared.GetTime(),
	}

	if rand.Float32() > shared.PCT_POST {
		req, err = http.Post(shared.WEBSERVER_URL, "application/json", bytes.NewBuffer([]byte(`{"message":"Buy cheese and bread for breakfast."}`)))
		res.CallType = "Post"
	} else {
		req, err = http.Get(shared.WEBSERVER_URL)
		res.CallType = "Get"
	}

	res.End = shared.GetTime()

	if err != nil {
		return nil
	} else {
		req.Body.Close()
		return res
	}
}

func RunTest(clients int, seconds int) chan *shared.Result {
	results := make(chan *shared.Result, seconds*100000*clients)
	closed := false

	for i := 0; i < clients; i++ {
		go func(j int) {
			for {
				if r := Query(); r == nil {
					continue
				} else if closed {
					return
				} else {
					r.ClientNum = j
					results <- r
				}
			}
		}(i)
	}

	<-time.After(time.Duration(seconds) * time.Second)
	close(results)
	closed = true
	return results
}

// Write out results as csv. Each line has the form: clientID,start,end,duration,type
func Output(clients, requests int, res chan *shared.Result, fname string) {
	f, err := os.Create(fmt.Sprintf("%s%dc-%dr", fname, clients, requests))
	shared.CheckErr(err)

	for r := range res {
		f.Write([]byte(fmt.Sprintf("%d,%d,%d,%d,%s\n",
			r.ClientNum,
			r.Start,
			r.End,
			r.End-r.Start,
			r.CallType)))
	}

	f.Close()
}

func main() {
	shared.LoadWindowsTimer()

	CLIENTS, err := strconv.Atoi(os.Args[1])
	shared.CheckErr(err)
	REQUESTS, e := strconv.Atoi(os.Args[2])
	shared.CheckErr(e)
	OUTPUT_DIR := os.Args[3]

	server := StartServer()
	results := RunTest(CLIENTS, REQUESTS)
	server.Close()

	Output(CLIENTS, REQUESTS, results, OUTPUT_DIR)
}
