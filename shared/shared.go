package shared

// The commented out portions are windows refs that dont compile on linux well,
// or at all

import (
	"fmt"
	"runtime"
	// _"syscall"
	"time"
	// _"unsafe"
)

const (
	PCT_POST           = 1 // 0.5 // Percentage of calls that are post requests
	WEBSERVER_TEMPLATE = "http://localhost:%s/reminders"
	IMGSERVER_URL      = "http://localhost/"
)

var (
	WinPreciseFileTime uintptr
	// Win32              syscall.Handle

	PORT          = "12345"
	WEBSERVER_URL string
)

type Result struct {
	ClientNum int
	Start     int64
	End       int64
	CallType  string
}

func init() {
	WEBSERVER_URL = fmt.Sprintf(WEBSERVER_TEMPLATE, PORT)
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

	/*
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
	*/

	return nil
}

// Returns UTC time in microseconds. If on windows, behavior is undefined if LoadWindowsTimer has not already been called
func GetTime() int64 {
	if runtime.GOOS == "windows" {
		var now int64
		// syscall.Syscall(WinPreciseFileTime, 1, uintptr(unsafe.Pointer(&now)), 0, 0)

		// GetSystemTimePreciseAsFileTime returns results in 100s of ns-- convert to us
		return now / 10
	} else {
		return time.Now().UnixNano() / 1e3
	}
}
