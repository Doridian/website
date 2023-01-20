package main

import (
	"fmt"
	"io"
	"io/fs"
	"log"
	"math/rand"
	"net/http"
	"os"
	"path"
	"strconv"
	"strings"
	"time"
)

var epaperDir = os.Getenv("EPAPER_DIR")
var epaperFiles []fs.DirEntry

const minRandBuffer = 3

var minRandBufferCur = 3

type HTTPErroringHandlerFunc = func(w http.ResponseWriter, r *http.Request) error

type ErroringHTTPHandler struct {
	subHandler HTTPErroringHandlerFunc
}

func (h *ErroringHTTPHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	err := h.subHandler(w, r)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte("Internal Server Error"))
	}
}

func ePaperImageHandler(w http.ResponseWriter, r *http.Request) error {
	token := r.URL.Query().Get("token")

	sequenceStr := strings.Split(token, ",")
	sequence := make([]int, 0, len(sequenceStr))
	for _, s := range sequenceStr {
		i, err := strconv.Atoi(s)
		if err != nil || i < 0 || i >= len(epaperFiles) {
			continue
		}
		sequence = append(sequence, i)
	}

	if len(sequence) <= minRandBufferCur {
		newPerm := rand.Perm(len(epaperFiles))
		if minRandBufferCur > 1 && len(sequence) > 0 && newPerm[0] == sequence[len(sequence)-1] {
			newPerm[0], newPerm[len(newPerm)-1] = newPerm[len(newPerm)-1], newPerm[0]
		}
		sequence = append(sequence, newPerm...)
	}

	sequenceStr = make([]string, 0, len(sequence))
	for _, i := range sequence {
		sequenceStr = append(sequenceStr, strconv.Itoa(i))
	}

	fileObject := epaperFiles[sequence[0]]
	fileName := fileObject.Name()

	fileInfo, err := fileObject.Info()
	if err != nil {
		log.Printf("Error getting ePaper file info: %v", err)
		return err
	}
	file, err := os.Open(path.Join(epaperDir, fileName))
	if err != nil {
		log.Printf("Error getting ePaper file handle: %v", err)
		return err
	}

	w.Header().Add("Content-Type", "application/octet-stream")
	w.Header().Add("Content-Disposition", fmt.Sprintf("attachment; filename=%s", fileName))
	w.Header().Add("Content-Length", fmt.Sprintf("%d", fileInfo.Size()))
	w.Header().Add("Token", strings.Join(sequenceStr[1:], ","))
	w.WriteHeader(http.StatusOK)
	_, err = io.Copy(w, file)
	if err != nil {
		log.Printf("Error copying ePaper file data: %v", err)
		return err
	}

	return nil
}

func loadFileList() {
	newEpaperFiles, err := os.ReadDir(epaperDir)
	if err != nil {
		panic(err)
	}

	newEpaperFilesFiltered := make([]fs.DirEntry, 0, len(newEpaperFiles))
	for _, file := range newEpaperFiles {
		if file.IsDir() || file.Name()[0] == '.' {
			continue
		}
		newEpaperFilesFiltered = append(newEpaperFilesFiltered, file)
	}

	epaperFiles = newEpaperFilesFiltered

	minRandBufferCur = minRandBuffer
	if minRandBufferCur > len(epaperFiles) {
		minRandBufferCur = len(epaperFiles)
	}
}

func main() {
	if epaperDir == "" {
		epaperDir = "epaper"
	}

	rand.Seed(time.Now().UnixNano())

	loadFileList()

	http.Handle("/api/e-paper-image", &ErroringHTTPHandler{subHandler: ePaperImageHandler})

	log.Print("Server ready, starting listener!")
	log.Fatal(http.ListenAndServe("127.0.0.1:8080", nil))
}
