function addSubjectRow() {
    const container = document.getElementById("rows-container");
    const template = document.getElementById("row-template");
    
    const newRow = template.firstElementChild.cloneNode(true);
    
    container.appendChild(newRow);
}

function removeRow(button) {
    const row = button.parentElement;
    row.remove();
}