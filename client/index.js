import {addDownloadLink, addProject, updateProjectStatus} from "./dom.js";

addEventListener("DOMContentLoaded", (event) => {
    setupUploadForm()
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
            poll_status(projectID)
        }).catch((e) => {
            console.error("err:", e)
        })
    }
}

function poll_status(projectID) {
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
                        poll_status(projectID)
                        break;
                    case "Succeeded":
                        addDownloadLink(projectID, `${apiURL}/projects/${projectID}/download`)
                        break;
                    default:
                        console.warn("unexpected status:", status);
                        poll_status(projectID);
                }
            })
            .catch((err) => {
                console.error("failed to check project status: ", err)
                poll_status(projectID)
            })
    }, 2000)
}
