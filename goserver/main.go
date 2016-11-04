package main

import (
	"bytes"
	"fmt"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"
)

const (
	PCT_POST = 0.5 // Percentage of calls that are post requests
	URL      = "http://localhost:8080/reminders"
)

type Result struct {
	ClientNum int
	Start     time.Time
	End       time.Time
	CallType  string
}

func Query() *Result {
	var req *http.Response
	var err error

	res := &Result{
		Start: time.Now(),
	}

	if rand.Float32() > PCT_POST {
		req, err = http.Post(URL, "application/json", bytes.NewBuffer([]byte(`{"message":"Buy cheese and bread for breakfast."}`)))
		res.CallType = "Post"
	} else {
		req, err = http.Get(URL)
		res.CallType = "Get"
	}

	res.End = time.Now()
	checkerr(err)
	req.Body.Close()
	return res
}

func RunTest(clients int, requests int) chan *Result {
	wg := &sync.WaitGroup{}
	wg.Add(clients)
	results := make(chan *Result, requests*clients)

	for i := 0; i < clients; i++ {
		go func(j int) {
			for q := 0; q < requests; q++ {
				r := Query()
				r.ClientNum = j
				results <- r
			}

			wg.Done()
		}(i)
	}

	wg.Wait()
	close(results)
	return results
}

// Write out results as csv. Each line has the form: clientID,start,end,duration,type
func Output(clients, requests int, res chan *Result, fname string) {
	f, err := os.Create(fmt.Sprintf("%s/%dc-%dr", fname, clients, requests))
	checkerr(err)

	for r := range res {
		f.Write([]byte(fmt.Sprintf("%d,%d,%d,%d,%s\n", r.ClientNum, r.Start.Nanosecond()/1e3, r.End.Nanosecond()/1e3,
			r.End.Sub(r.Start).Nanoseconds()/1e3, r.CallType)))
	}

	f.Close()
}

func main() {
	CLIENTS, err := strconv.Atoi(os.Args[1])
	checkerr(err)
	REQUESTS, e := strconv.Atoi(os.Args[2])
	checkerr(e)
	OUTPUT_DIR := os.Args[3]

	server := StartServer()
	results := RunTest(CLIENTS, REQUESTS)
	server.Close()

	Output(CLIENTS, REQUESTS, results, OUTPUT_DIR)
}
