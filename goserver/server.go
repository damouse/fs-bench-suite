package main

import (
	"net"
	"net/http"
	"time"

	"github.com/ant0ine/go-json-rest/rest"
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

func checkerr(err error) {
	if err != nil {
		panic(err)
	}
}

func StartServer() net.Listener {

	i := Impl{}
	i.InitDB()
	i.InitSchema()

	api := rest.NewApi()
	// api.Use(rest.DefaultDevStack...)
	api.Use(&rest.TimerMiddleware{},
		&rest.RecorderMiddleware{},
		&rest.PoweredByMiddleware{},
		&rest.RecoverMiddleware{})

	router, err := rest.MakeRouter(
		rest.Get("/reminders", i.GetAllReminders),
		rest.Post("/reminders", i.PostReminder),
		rest.Get("/reminders/:id", i.GetReminder),
		rest.Put("/reminders/:id", i.PutReminder),
		rest.Delete("/reminders/:id", i.DeleteReminder),
	)

	checkerr(err)
	api.SetApp(router)

	l, err := net.Listen("tcp", ":8080")
	checkerr(err)

	go func() {
		http.Serve(l, api.MakeHandler())
	}()

	return l

}

type Reminder struct {
	Id        int64     `json:"id"`
	Message   string    `sql:"size:1024" json:"message"`
	CreatedAt time.Time `json:"createdAt"`
	UpdatedAt time.Time `json:"updatedAt"`
}

type Impl struct {
	DB *gorm.DB
}

func (i *Impl) InitDB() {
	var err error
	i.DB, err = gorm.Open("postgres", "host=localhost user=postgres dbname=mydb sslmode=disable password=postgres")
	checkerr(err)

	i.DB.Delete(Reminder{})
	i.DB.LogMode(false)
}

func (i *Impl) InitSchema() {
	i.DB.AutoMigrate(&Reminder{})
}

func (i *Impl) GetAllReminders(w rest.ResponseWriter, r *rest.Request) {
	reminders := []Reminder{}
	i.DB.Find(&reminders)
	w.WriteJson(&reminders)
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

func (i *Impl) PutReminder(w rest.ResponseWriter, r *rest.Request) {
	id := r.PathParam("id")
	reminder := Reminder{}

	if i.DB.First(&reminder, id).Error != nil {
		rest.NotFound(w, r)
		return
	}

	updated := Reminder{}

	if err := r.DecodeJsonPayload(&updated); err != nil {
		rest.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	reminder.Message = updated.Message

	if err := i.DB.Save(&reminder).Error; err != nil {
		rest.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteJson(&reminder)
}

func (i *Impl) DeleteReminder(w rest.ResponseWriter, r *rest.Request) {
	id := r.PathParam("id")
	reminder := Reminder{}

	if i.DB.First(&reminder, id).Error != nil {
		rest.NotFound(w, r)
		return
	}

	if err := i.DB.Delete(&reminder).Error; err != nil {
		rest.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}
