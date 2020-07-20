function fancyTables() {
    const tables = document.getElementsByTagName("table");

    for (let i = 0; i < tables.length; i++) {
        let table_id = tables[i].getAttribute("id")
        let table = $("#" + table_id).DataTable({
            dom: '<Bf<t>lip>',
            paging: false,
            searching: false,
            info: false,
            ordering: false,
            buttons: ['copy', 'csv', 'excel', 'print']
            });

    }
}

function fancyTablesNoButtons() {
    const tables = document.getElementsByTagName("table");

    for (let i = 0; i < tables.length; i++) {
        let table_id = tables[i].getAttribute("id")
        let table = $("#" + table_id).DataTable({
            dom: '<f<t>lip>',
            paging: false,
            searching: false,
            info: false,
            ordering: false,
            });

    }
}

function fetchJSON(url, callback) {
    let httpRequest = new XMLHttpRequest();
    httpRequest.onreadystatechange = function() {
        if (httpRequest.readyState === 4) {
            if (httpRequest.status === 200) {
                let data = JSON.parse(httpRequest.responseText);
                if (callback) callback(data);
            }
        }
    };
    httpRequest.open('GET', url);
    httpRequest.send(); 
}
