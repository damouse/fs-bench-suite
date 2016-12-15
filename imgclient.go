package main

import (
	"fmt"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"

	"./shared"
)

func Query(i int) *shared.Result {
	res := &shared.Result{
		Start: shared.GetTime(),
	}

	target := fmt.Sprintf("%s%d.jpg", shared.IMGSERVER_URL, i)
	response, e := http.Get(target)
	res.End = shared.GetTime()

	shared.CheckErr(e)
	response.Body.Close()
	return res
}

func RunTest(clients int, seconds int) chan *shared.Result {
	results := make(chan *shared.Result, seconds*100000*clients)
	closed := false
	var wg sync.WaitGroup
	wg.Add(clients)

	for i := 0; i < clients; i++ {
		go func(j int) {
			var res []*shared.Result

			for {
				if r := Query(j); r == nil {
					continue
				} else if closed {
					for _, r := range res {
						results <- r
					}

					// Signal close and return
					wg.Done()
					return
				} else {
					r.ClientNum = j
					results <- r
					time.Sleep(20 * time.Millisecond)
				}
			}
		}(i)
	}

	// wg.Wait()
	// close(results)
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
	os.Exit(0)
}

func main() {
	shared.LoadWindowsTimer()

	CLIENTS, err := strconv.Atoi(os.Args[1])
	shared.CheckErr(err)
	SECONDS, e := strconv.Atoi(os.Args[2])
	shared.CheckErr(e)
	OUTPUT_DIR := os.Args[3]

	fmt.Printf("Imgserver %v clients %v seconds, output: %v\n", CLIENTS, SECONDS, OUTPUT_DIR)

	results := RunTest(CLIENTS, SECONDS)
	Output(CLIENTS, SECONDS, results, OUTPUT_DIR)
	fmt.Println("Done")
}
