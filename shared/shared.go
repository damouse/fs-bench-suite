package shared

import (
	"fmt"
	"syscall"
	"time"
	"unsafe"
)

const URL = "http://localhost/"

var (
	WinPreciseFileTime uintptr
	Win32              syscall.Handle
)

func CheckErr(err error) {
	if err != nil {
		panic(err.Error())
	}
}

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

func LoadWindowsTimer() error {
	var e error
	Win32, e = syscall.LoadLibrary("kernel32.dll")
	CheckErr(e)

	WinPreciseFileTime, e = syscall.GetProcAddress(Win32, "GetSystemTimePreciseAsFileTime")
	CheckErr(e)

	if WinPreciseFileTime == 0 {
		return fmt.Errorf("Unable to get precise system time")
	} else {
		return nil
	}
}

// Returns UTC time in microseconds. Behavior is undefined if LoadWindowsTimer has not already been called
func GetTime() int64 {
	var now int64
	syscall.Syscall(WinPreciseFileTime, 1, uintptr(unsafe.Pointer(&now)), 0, 0)
	return now
}

func SomeOperation() {
	q := 0

	for i := 0; i < 100000; i++ {
		q += i
	}

	// fmt.Println("Done")
}

func Hello() {
	e := LoadWindowsTimer()
	CheckErr(e)

	firstNow := time.Now()
	SomeOperation()
	secondNow := time.Now()

	firstTimefile := GetTime()
	SomeOperation()
	secondTimefile := GetTime()

	firstClock := Clock()
	SomeOperation()
	secondClock := Clock()

	// timeFromTS := time.Unix(0, ts)
	// tm := time.Unix(0, firstTimefile)
	// fmt.Println(tm)

	fmt.Printf("Now: %v, Timefile: %v, GetPerformanceCounter: %v, Timefile/QPC: %v\n",
		secondNow.Sub(firstNow),
		(secondTimefile-firstTimefile)/10,
		(secondClock-firstClock).Nanoseconds()/1e3,
		(secondClock-firstClock).Nanoseconds()/(secondTimefile-firstTimefile),
	)

	fmt.Printf("FirstTF: %v, FirstClock: %v\n", firstTimefile, firstClock.Nanoseconds()/1e2)
}
