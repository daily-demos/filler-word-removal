import {addDailyRecording, addDownloadLink, addProject, updateProjectStatus} from "./dom.js";

addEventListener("DOMContentLoaded", (event) => {
    setupUploadForm()
    setupRecordingsFetchBtn()
});

const apiURL = 'http://127.0.0.1:5000'

function setupUploadForm() {
    const form = document.getElementById("uploadForm")
    form.onsubmit = (ev) => {
        ev.preventDefault();

        const video = document.getElementById("videoFile").files[0];
        const formData = new FormData();

        formData.append("file", video);
        fetch(`${apiURL}/upload`, {method: "POST", body: formData}).then((res) => {
            if (res.ok === false) {
                throw Error(`upload request failed: ${res.status}`)
            }
            return res.json()
        }).then((data) => {
            const projectID = data['project_id']
            addProject(projectID, data['name'])
            pollStatus(projectID)
        }).catch((e) => {
            console.error("Failed to process uploaded video:", e)
        })
    }
}

function setupRecordingsFetchBtn() {
    const btn = document.getElementById("fetchRecordings")
    btn.onclick = () => {
        fetch(`${apiURL}/recordings`, {method: "GET"}).then((res) => {
            if (res.ok === false) {
                throw Error(`upload request failed: ${res.status}`)
            }
            return res.json()
        }).then((data) => {
            console.log("DATA:", data);
            const recordings = data['recordings']
            for (let i = 0; i < recordings.length; i += 1) {
                const rec = recordings[i]
                addDailyRecording(rec['id'], rec['room_name'], rec['timestamp'], processDailyRecording)
            }

        }).catch((e) => {
            console.error("Failed to process uploaded video:", e)
        })
    }
}

function processDailyRecording(recordingID) {
    fetch(
        `${apiURL}/process_recording/${recordingID}`,
        {
            method: "POST",
        }).then((res) => {
        if (res.ok === false) {
            throw Error(`Recording processing failed: ${res.status}`)
        }
        return res.json()
    }).then((data) => {
        const projectID = data['project_id']
        addProject(projectID, data['name'])
        pollStatus(projectID)
    }).catch((e) => {
        console.error("Failed to process Daily recording:", e)
    })
}

function pollStatus(projectID) {
    setTimeout(() => {
        fetch(`${apiURL}/projects/${projectID}`)
            .then((res) => {
                if (!res.ok) {
                    throw Error(`status request failed: ${res.status}`)
                }
                return res.json()
            })
            .then((data) => {
                const status = data['status']
                const info = data['info']
                console.log("project status:", status)
                updateProjectStatus(projectID, status, info)
                switch (status) {
                    case "In progress":
                        pollStatus(projectID)
                        break;
                    case "Succeeded":
                        addDownloadLink(projectID, `${apiURL}/projects/${projectID}/download`)
                        break;
                    default:
                        console.warn("unexpected status:", status);
                        pollStatus(projectID);
                }
            })
            .catch((err) => {
                console.error("failed to check project status: ", err)
                pollStatus(projectID)
            })
    }, 2000)
}
