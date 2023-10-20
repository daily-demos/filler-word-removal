const projStatusCellIdx = 2;
const projInfoCellIdx = 3;
const projDownloadCellIdx = 4;

const hiddenClassName = 'hidden';

/**
 * Add a project to the Uploads table
 * @param id
 * @param name
 */
export function addUploadedProject(id, name) {
  const uploadsTable = getUploadsTable();

  const row = uploadsTable.insertRow(-1);
  row.id = id;

  const nameCell = row.insertCell(-1);
  nameCell.innerText = name;

  const idCell = row.insertCell(-1);
  idCell.innerText = id;

  const statusCell = row.insertCell(-1);
  statusCell.append(createSpinner());

  const infoCell = row.insertCell(-1);
  infoCell.append(createSpinner());

  const dlCell = row.insertCell(-1);
  dlCell.append(createSpinner());

  uploadsTable.classList.remove(hiddenClassName);
}

/**
 * Add a recording to the Recordings table
 * @param recordingID
 * @param roomName
 * @param timestamp
 * @param processFunc
 */
export function addDailyRecording(
  recordingID,
  roomName,
  timestamp,
  processFunc,
) {
  // Do not re-add if recording row already exists
  const existingRow = getProjectRow(null, recordingID)
  if (existingRow) return;

  const recordingTable = getRecordingsTable();

  const row = recordingTable.insertRow(-1);
  row.id = recordingID;

  const timestampCell = row.insertCell(-1);
  timestampCell.innerText = timestamp;

  const nameCell = row.insertCell(-1);
  nameCell.innerText = roomName;

  const statusCell = row.insertCell(-1);
  statusCell.innerText = 'Not started';

  // Empty info cell
  row.insertCell(-1);

  const controlCell = row.insertCell(-1);

  const processBtn = document.createElement('button');
  processBtn.classList.add('light-btn');
  processBtn.innerText = 'Process';
  processBtn.onclick = () => {
    processBtn.disabled = true;
    processFunc(recordingID);
    controlCell.innerText = '';
    controlCell.append(createSpinner());
  };
  controlCell.append(processBtn);

  recordingTable.classList.remove(hiddenClassName);
}

/**
 * Update the status of a recording, whether it is in the Uploads or the Recordings table
 * @param id
 * @param status
 * @param info
 * @param isDailyRecording
 */
export function updateProjectStatus(projectID, status, info, recordingID) {
  const row = getProjectRow(projectID, recordingID);

  const statusCell = row.cells[projStatusCellIdx];
  statusCell.innerText = status;

  const infoCell = row.cells[projInfoCellIdx];
  infoCell.innerText = info;
}

export function addDownloadLink(projectID, link, recordingID) {
  const project = getProjectRow(projectID, recordingID);
  const dlCell = project.cells[projDownloadCellIdx];
  dlCell.innerText = '';
  const a = document.createElement('a');
  a.href = link;
  a.download = 'true';
  a.innerText = 'Download Output';
  dlCell.append(a);
}

function getUploadsTable() {
  return document.getElementById('uploads');
}

function getRecordingsTable() {
  return document.getElementById('dailyRecordings');
}

/**
 * Retrieve project row from either Uploads or Recordings table
 * @param id
 * @param isDailyRecording
 * @returns {HTMLTableRowElement}
 */
function getProjectRow(projectID, recordingID) {
  let ele;
  let table;
  if (recordingID) {
    ele = document.getElementById(recordingID);
    table = getRecordingsTable();
  } else {
    ele = document.getElementById(projectID);
    table = getUploadsTable();
  }

  const rowIdx = ele?.rowIndex;
  if (!rowIdx) return null;
  return table.rows[rowIdx];
}

/**
 * Create a spinner element to show processing in progress.
 * @returns {HTMLDivElement}
 */
function createSpinner() {
  const ele = document.createElement('div');
  ele.className = 'spinner';
  return ele;
}
