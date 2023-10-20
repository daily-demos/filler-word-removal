import {
  addDailyRecording,
  addDownloadLink,
  addUploadedProject,
  updateProjectStatus,
} from './dom.js';

window.addEventListener('DOMContentLoaded', () => {
  setupUploadForm();
  setupRecordingsFetchBtn();
});

const apiURL = 'http://127.0.0.1:5000';

/**
 * Configures the manual file upload form
 */
function setupUploadForm() {
  const form = document.getElementById('uploadForm');
  form.onsubmit = (ev) => {
    ev.preventDefault();

    const video = document.getElementById('videoFile').files[0];
    const formData = new FormData();
    formData.append('file', video);

    // Upload the selected file to the server. This will begin processing the file
    // to remove filler words.
    fetch(`${apiURL}/upload`, { method: 'POST', body: formData })
      .then((res) => {
        if (res.ok === false) {
          throw Error(`upload request failed: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        // Retrieve project ID from server response and begin polling status.
        const projectID = data.project_id;

        // Update the DOM to show the new project
        addUploadedProject(projectID, data.name);
        pollStatus(projectID);
      })
      .catch((e) => {
        console.error('Failed to process uploaded video:', e);
      });
  };
}

/**
 * Configures fetching Daily recordings
 */
function setupRecordingsFetchBtn() {
  const btn = document.getElementById('fetchRecordings');
  btn.onclick = () => {
    // Fetch all recordings from the server
    fetch(`${apiURL}/recordings`, { method: 'GET' })
      .then((res) => {
        if (res.ok === false) {
          throw Error(`upload request failed: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        // Add each fetched recording to the recordings table in the DOM
        const { recordings } = data;
        for (let i = 0; i < recordings.length; i += 1) {
          const rec = recordings[i];
          addDailyRecording(
            rec.id,
            rec.room_name,
            rec.timestamp,
            processDailyRecording,
          );
        }
      })
      .catch((e) => {
        console.error('Failed to process uploaded video:', e);
      });
  };
}

/**
 * Processes a specified Daily recording to remove filler words
 * @param recordingID
 */
function processDailyRecording(recordingID) {
  // Begin processing Daily recording to remove filler words
  fetch(`${apiURL}/process_recording/${recordingID}`, {
    method: 'POST',
  })
    .then((res) => {
      if (res.ok === false) {
        throw Error(`Recording processing failed: ${res.status}`);
      }
      return res.json();
    })
    .then((data) => {
      const projectID = data.project_id;
      // Begin polling status
      pollStatus(projectID, recordingID);
    })
    .catch((e) => {
      console.error('Failed to process Daily recording:', e);
    });
}

/**
 * Check the status of a processing project
 * @param projectID
 * @param isRecording
 */
function pollStatus(projectID, recordingID = null) {
  setTimeout(() => {
    // Fetch status of the given project from the server
    fetch(`${apiURL}/projects/${projectID}`)
      .then((res) => {
        if (!res.ok) {
          throw Error(`status request failed: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        const { status } = data;
        const { info } = data;

        // Update status in the DOM
        updateProjectStatus(projectID, status, info, recordingID);
        switch (status) {
          case 'In progress':
            pollStatus(projectID, recordingID);
            break;
          case 'Succeeded':
            addDownloadLink(
              projectID,
              `${apiURL}/projects/${projectID}/download`,
              recordingID,
            );
            break;
          case 'Failed':
            break;
          default:
            console.warn('unexpected status:', status);
            pollStatus(projectID, recordingID);
        }
      })
      .catch((err) => {
        console.error('failed to check project status: ', err);
        pollStatus(projectID, recordingID);
      });
  }, 2000);
}
