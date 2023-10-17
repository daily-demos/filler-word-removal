const projStatusCellIdx = 2;
const projInfoCellIdx = 3;
const projDownloadCellIdx = 4;

const hiddenClassName = 'hidden';

export function addProject(id, name) {
  const projectsTable = getProjectsTable();

  const row = projectsTable.insertRow(-1);
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

  projectsTable.classList.remove(hiddenClassName);
}

export function addDailyRecording(id, roomName, timestamp, processFunc) {
  const recordingTable = getRecordingsTable();

  const row = recordingTable.insertRow(-1);
  row.id = id;

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
    processFunc(id);
    controlCell.innerText = '';
    controlCell.append(createSpinner());
  };
  controlCell.append(processBtn);

  recordingTable.classList.remove(hiddenClassName);
}

export function updateProjectStatus(
  id,
  status,
  info,
  isDailyRecording = false,
) {
  const row = getProjectRow(id, isDailyRecording);

  const statusCell = row.cells[projStatusCellIdx];
  statusCell.innerText = status;

  const infoCell = row.cells[projInfoCellIdx];
  infoCell.innerText = info;
}

export function addDownloadLink(id, link) {
  const project = getProjectRow(id);
  const dlCell = project.cells[projDownloadCellIdx];
  dlCell.innerText = '';
  const a = document.createElement('a');
  a.href = link;
  a.download = 'true';
  a.innerText = 'Download Output';
  dlCell.append(a);
}

function getProjectsTable() {
  return document.getElementById('projectsTable');
}

function getProjectRow(id, isDailyRecording) {
  const ele = document.getElementById(id);
  const rowIdx = ele.rowIndex;
  let table;
  if (!isDailyRecording) {
    table = getRecordingsTable();
  } else {
    table = getRecordingsTable();
  }
  return table.rows[rowIdx];
}

function getRecordingsTable() {
  return document.getElementById('dailyRecordings');
}

function createSpinner() {
  const ele = document.createElement('div');
  ele.className = 'spinner';
  return ele;
}
