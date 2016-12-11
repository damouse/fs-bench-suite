package main

import (
	"fmt"
	"net/http"
	"os"
	"strconv"
	"syscall"
	"time"
	"unsafe"
)

const URL = "http://localhost/"

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

func checkerr(err error) {
	if err != nil {
		fmt.Println("Some error has occured")
		panic(err.Error())
	}
}

type Result struct {
	ClientNum  int
	ImageIndex int
	Start      time.Duration
	End        time.Duration
}

func Query(i int, unique bool) *Result {
	res := &Result{
		Start:      Clock(),
		ImageIndex: i,
	}

	target := fmt.Sprintf("%s%d.jpg", URL, i)
	if !unique {
		target = URL + "1.png"
	}

	response, e := http.Get(target)
	res.End = Clock()

	if e != nil {
		return nil
	} else {
		response.Body.Close()
		return res
	}
}

func RunTest(clients int, seconds int, unique bool) chan *Result {
	results := make(chan *Result, seconds*100000*clients)
	closed := false

	for i := 0; i < clients; i++ {
		go func(j int) {
			for {
				if r := Query(j, unique); r == nil {
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

	// wg.Wait()
	// close(results)
	<-time.After(time.Duration(seconds) * time.Second)
	close(results)
	closed = true
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
			r.Start.Nanoseconds()/1e3,
			r.End.Nanoseconds()/1e3,
			(r.End-r.Start).Nanoseconds()/1e3,
			r.ImageIndex)))
	}

	f.Close()
	os.Exit(0)
}

func main() {
	CLIENTS, err := strconv.Atoi(os.Args[1])
	checkerr(err)
	SECONDS, e := strconv.Atoi(os.Args[2])
	checkerr(e)
	UNIQUE, e := strconv.ParseBool(os.Args[3])
	checkerr(e)
	OUTPUT_DIR := os.Args[4]

	results := RunTest(CLIENTS, SECONDS, UNIQUE)
	Output(CLIENTS, SECONDS, results, UNIQUE, OUTPUT_DIR)
	fmt.Println("Done")
}
