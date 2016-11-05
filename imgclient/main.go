package main

import (
	"fmt"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"
)

const URL = "http://localhost/images/"

func checkerr(err error) {
	if err != nil {
		panic(err)
	}
}

type Result struct {
	ClientNum  int
	ImageIndex int
	Start      time.Time
	End        time.Time
}

func Query(i int, unique bool) *Result {
	res := &Result{
		Start:      time.Now(),
		ImageIndex: i,
	}

	target := fmt.Sprintf("%s%d.jpg", URL, i)
	if !unique {
		target = URL + "1.png"
	}

	response, e := http.Get(target)
	res.End = time.Now()

	checkerr(e)
	response.Body.Close()
	return res
}

func RunTest(clients int, requests int, unique bool) chan *Result {
	wg := &sync.WaitGroup{}
	wg.Add(clients)
	results := make(chan *Result, requests*clients)

	for i := 0; i < clients; i++ {
		go func(j int) {
			for q := 0; q < requests; q++ {
				r := Query(j, unique)
				r.ClientNum = j
				results <- r

				// fmt.Printf("Client %d request %d time %d\n", j, q, r.End.Sub(r.Start).Nanoseconds()/1e3)
			}

			wg.Done()
		}(i)
	}

	wg.Wait()
	close(results)
	return results
}

// Write out results as csv. Each line has the form: clientID,start,end,duration,type
func Output(clients, requests int, res chan *Result, unique bool, fname string) {
	isUnique := "unique"

	if !unique {
		isUnique = "shared"
	}

	f, err := os.Create(fmt.Sprintf("%s%dc-%dr-%s", fname, clients, requests, isUnique))
	checkerr(err)

	for r := range res {
		f.Write([]byte(fmt.Sprintf("%d,%d,%d,%d,%d\n",
			r.ClientNum,
			r.Start.Nanosecond()/1e3,
			r.End.Nanosecond()/1e3,
			r.End.Sub(r.Start).Nanoseconds()/1e3,
			r.ImageIndex)))
	}

	f.Close()
}

func main() {
	CLIENTS, err := strconv.Atoi(os.Args[1])
	checkerr(err)
	REQUESTS, e := strconv.Atoi(os.Args[2])
	checkerr(e)
	UNIQUE, e := strconv.ParseBool(os.Args[3])
	checkerr(e)
	OUTPUT_DIR := os.Args[4]

	results := RunTest(CLIENTS, REQUESTS, UNIQUE)
	Output(CLIENTS, REQUESTS, results, UNIQUE, OUTPUT_DIR)
}
