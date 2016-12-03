package main

import (
	"bytes"
	"fmt"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"syscall"
	"time"
	"unsafe"
)

var Clock func() time.Duration

// Windows specific timer. Go's default timer maxes out at 1ms accuracy, this has 1ns
// by calling directly into the win32 apis
func init() {
	QPCTimer := func() func() time.Duration {
		lib, _ := syscall.LoadLibrary("kernel32.dll")
		qpc, _ := syscall.GetProcAddress(lib, "QueryPerformanceCounter")
		qpf, _ := syscall.GetProcAddress(lib, "QueryPerformanceFrequency")
		if qpc == 0 || qpf == 0 {
			return nil
		}

		var freq, start uint64
		syscall.Syscall(qpf, 1, uintptr(unsafe.Pointer(&freq)), 0, 0)
		syscall.Syscall(qpc, 1, uintptr(unsafe.Pointer(&start)), 0, 0)
		if freq <= 0 {
			return nil
		}

		freqns := float64(freq) / 1e9

		return func() time.Duration {
			var now uint64
			syscall.Syscall(qpc, 1, uintptr(unsafe.Pointer(&now)), 0, 0)
			return time.Duration(float64(now-start) / freqns)
		}
	}

	if Clock = QPCTimer(); Clock == nil {
		// Fallback implementation
		start := time.Now()
		Clock = func() time.Duration { return time.Since(start) }
	}
}

const (
	PCT_POST = 0.5 // Percentage of calls that are post requests
	URL      = "http://localhost:8080/reminders"
)

type Result struct {
	ClientNum int
	Start     time.Duration
	End       time.Duration
	CallType  string
}

func Query() *Result {
	var req *http.Response
	var err error

	res := &Result{
		Start: Clock(),
	}

	if rand.Float32() > PCT_POST {
		req, err = http.Post(URL, "application/json", bytes.NewBuffer([]byte(`{"message":"Buy cheese and bread for breakfast."}`)))
		res.CallType = "Post"
	} else {
		req, err = http.Get(URL)
		res.CallType = "Get"
	}

	res.End = Clock()

	if err != nil {
		return nil
	} else {
		req.Body.Close()
		return res
	}
}

func RunTest(clients int, seconds int) chan *Result {
	results := make(chan *Result, seconds*100000*clients)
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
func Output(clients, requests int, res chan *Result, fname string) {
	f, err := os.Create(fmt.Sprintf("%s%dc-%dr", fname, clients, requests))
	checkerr(err)

	for r := range res {
		f.Write([]byte(fmt.Sprintf("%d,%d,%d,%d,%s\n",
			r.ClientNum,
			r.Start.Nanoseconds()/1e3,
			r.End.Nanoseconds()/1e3,
			(r.End-r.Start).Nanoseconds()/1e3,
			r.CallType)))
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
