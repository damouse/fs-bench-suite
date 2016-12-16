package main

import (
	"bytes"
	"fmt"
	"net"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"

	"./shared"
	"github.com/ant0ine/go-json-rest/rest"
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

// var payload = bytes.NewBuffer([]byte(`{"message":"Buy cheese and bread for breakfast."}`))

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

	l, err := net.Listen("tcp", ":"+shared.PORT)
	shared.CheckErr(err)

	go func() {
		http.Serve(l, api.MakeHandler())
		// shared.CheckErr(e)
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

	res := &shared.Result{}
	res.Start = shared.GetTime()
	req, err = http.Post(shared.WEBSERVER_URL, "application/json", bytes.NewBuffer([]byte(`{"message":"Buy cheese and bread for breakfast."}`)))
	res.End = shared.GetTime()

	// fmt.Printf("")

	shared.CheckErr(err)
	req.Body.Close()
	return res
}

func RunTest(clients int, seconds int) chan *shared.Result {
	// Effectively make the channel's buffer infinite-- dont want it to block
	results := make(chan *shared.Result, seconds*100000*clients)
	closed := false
	var wg sync.WaitGroup
	wg.Add(clients)

	for i := 0; i < clients; i++ {
		go func(j int) {
			var res []*shared.Result

			for {
				if r := Query(); r == nil {
					continue
				} else if closed {
					// Its time to stop issueing requests. Push results onto the channel
					for _, r := range res {
						results <- r
					}

					// Signal close and return
					wg.Done()
					return

				} else {
					r.ClientNum = j
					res = append(res, r)
					time.Sleep(20 * time.Millisecond)
				}
			}
		}(i)
	}

	<-time.After(time.Duration(seconds) * time.Second)
	closed = true
	wg.Wait()
	close(results)
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

	fmt.Printf("Webserver %v clients %v seconds, output: %v\n", CLIENTS, REQUESTS, OUTPUT_DIR)

	server := StartServer()
	results := RunTest(CLIENTS, REQUESTS)
	server.Close()

	Output(CLIENTS, REQUESTS, results, OUTPUT_DIR)
	os.Exit(0)

	// for i := 0; i < 100; i++ {
	// 	a := shared.GetTime()
	// 	c := time.Now()
	// 	time.Sleep(1 * time.Microsecond)
	// 	d := time.Now()
	// 	b := shared.GetTime()

	// 	fmt.Printf("%d %v, %v\n", i, b-a, d.Sub(c).Nanoseconds())
	// }
}
