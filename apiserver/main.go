package main

import (
	"fmt"
	"io"
	"log"
	"math/rand"
	"net/http"
	"os"
	"path"
	"strconv"
	"strings"
	"time"
)

const minRandBuffer = 3

type epaperFile struct {
	Name string
	Size int64
}

var epaperDir = os.Getenv("EPAPER_DIR")
var epaperFiles []*epaperFile

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

	epaperFilesHold := epaperFiles // So we can live reload!
	epaperFilesHoldLen := len(epaperFilesHold)

	sequenceStr := strings.Split(token, ",")
	sequence := make([]int, 0, len(sequenceStr))
	for _, s := range sequenceStr {
		i, err := strconv.Atoi(s)
		if err != nil || i < 0 || i >= epaperFilesHoldLen {
			continue
		}
		sequence = append(sequence, i)
	}
	sequenceLen := len(sequence)

	minRandBufferCur := minRandBuffer
	if minRandBufferCur > epaperFilesHoldLen {
		minRandBufferCur = epaperFilesHoldLen
	}

	if sequenceLen <= minRandBufferCur {
		newPerm := rand.Perm(epaperFilesHoldLen)
		if minRandBufferCur > 1 && sequenceLen > 0 && newPerm[0] == sequence[sequenceLen-1] {
			newPerm[0], newPerm[epaperFilesHoldLen-1] = newPerm[epaperFilesHoldLen-1], newPerm[0]
		}
		sequence = append(sequence, newPerm...)
	}

	sequenceStr = make([]string, 0, sequenceLen)
	for _, i := range sequence {
		sequenceStr = append(sequenceStr, strconv.Itoa(i))
	}

	fileObject := epaperFilesHold[sequence[0]]

	file, err := os.Open(path.Join(epaperDir, fileObject.Name))
	if err != nil {
		log.Printf("Error getting ePaper file handle: %v", err)
		return err
	}

	w.Header().Add("Content-Type", "application/octet-stream")
	w.Header().Add("Content-Disposition", fmt.Sprintf("attachment; filename=%s", fileObject.Name))
	w.Header().Add("Content-Length", fmt.Sprintf("%d", fileObject.Size))
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
	newEpaperFilesDirEnt, err := os.ReadDir(epaperDir)
	if err != nil {
		panic(err)
	}

	newEpaperFiles := make([]*epaperFile, 0, len(newEpaperFilesDirEnt))
	for _, file := range newEpaperFilesDirEnt {
		if file.IsDir() || file.Name()[0] == '.' {
			continue
		}
		fileInfo, err := file.Info()
		if err != nil {
			log.Printf("Error getting ePaper file %s info: %v", file.Name(), err)
			continue
		}
		newEpaperFiles = append(newEpaperFiles, &epaperFile{
			Name: file.Name(),
			Size: fileInfo.Size(),
		})
	}

	log.Printf("Found %d files!", len(newEpaperFiles))

	epaperFiles = newEpaperFiles
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
