const projNameCellIdx = 0;
const projIdCellIdx = 1;
const projStatusCellIdx = 2;
const projInfoCellIdx = 3;
const projDownloadCellIdx = 4;

export function addProject(id, name) {
    const projectsTable = getProjectsTable()

    const row = projectsTable.insertRow(-1)
    row.id = id;

    const nameCell = row.insertCell(-1);
    nameCell.innerText = name;

    const idCell = row.insertCell(-1);
    idCell.innerText = id;

    const statusCell = row.insertCell(-1)
    statusCell.append(createSpinner());

    const infoCell = row.insertCell(-1);
    infoCell.append(createSpinner());

    const dlCell = row.insertCell(-1);
    dlCell.append(createSpinner());
}

export function updateProjectStatus(id, status, info) {
    const row = getProjectRow(id);

    const statusCell = row.cells[projStatusCellIdx];
    statusCell.innerText = status;

    const infoCell = row.cells[projInfoCellIdx];
    infoCell.innerText = info;
}

export function removeAllProjects() {
    const projects = getProjectsEle();
    projects.innerText = "";
}

export function addDownloadLink(id, link) {
    const project = getProjectRow(id);
    const dlCell = project.cells[projDownloadCellIdx]
    dlCell.innerText = "";
    const a = document.createElement("a");
    a.href = link;
    a.download = "true";
    a.innerText = "Download Output"
    dlCell.append(a);
}

function getProjectsEle() {
    return document.getElementById("projects")
}

function getProjectsTable() {
    return document.getElementById("projectsTable")
}

function getProjectRow(id) {
    const ele = document.getElementById(id);
    const rowIdx = ele.rowIndex;
    const table = getProjectsTable()
    return table.rows[rowIdx]
}


function createSpinner() {
    const ele = document.createElement('div');
    ele.className = 'spinner';
    return ele;
}
