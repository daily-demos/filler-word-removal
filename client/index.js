addEventListener("DOMContentLoaded", (event) => {
    setupUploadForm()

});

function setupUploadForm() {
    const form = document.getElementById("uploadForm")
    form.onsubmit = (ev) => {
        ev.preventDefault();

        const video = document.getElementById("videoFile").files[0];
        const formData = new FormData();

        formData.append("file", video);
        fetch('http://127.0.0.1:5000/upload', {method: "POST", body: formData}).then((res) => {
            console.log("res:", res)
        }).catch((e) => {
            console.error("err:", e)
        })
    }
}