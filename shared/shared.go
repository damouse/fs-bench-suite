package shared

import (
	"fmt"
	"runtime"
	"syscall"
	"time"
	"unsafe"
)

const (
	PCT_POST      = 0.5 // Percentage of calls that are post requests
	WEBSERVER_URL = "http://localhost:8080/reminders"
	IMGSERVER_URL = "http://localhost/"
)

var (
	WinPreciseFileTime uintptr
	Win32              syscall.Handle
)

type Result struct {
	ClientNum int
	Start     int64
	End       int64
	CallType  string
}

func CheckErr(err error) {
	if err != nil {
		panic(err.Error())
	}
}

// Load the timer on windows
func LoadWindowsTimer() error {
	if runtime.GOOS != "windows" {
		return nil
	}

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

// Returns UTC time in microseconds. If on windows, behavior is undefined if LoadWindowsTimer has not already been called
func GetTime() int64 {
	if runtime.GOOS == "windows" {
		var now int64
		syscall.Syscall(WinPreciseFileTime, 1, uintptr(unsafe.Pointer(&now)), 0, 0)

		// Convert to us. GetSystemTimePrecise returns results in
		return now / 10
	} else {
		return int64(time.Now().Nanosecond()) / 1e3
	}
}
