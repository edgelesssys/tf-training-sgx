package main

import (
	"fmt"
	"os"

	"golang.org/x/sys/unix"
)

func main() {
	fmt.Println("Calling into main process")
	unix.Exec("/usr/bin/python3.8", []string{
		"python3", "training.py",
		"--log_dir=/train",
		"--checkpoint_dir=/train",
	}, os.Environ())
}
