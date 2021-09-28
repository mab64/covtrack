'use strict';

var cnt = 1;
var aData = [];
var aHead = [];


window.onload = function() {
	// Setup the GO button click handler.
	document.getElementById("btnGo").onclick = function() {
		if (document.getElementById('op_type1').checked) {
			showData();
		} else {
			updateData();
		}
	}
}


function showData() {
	/* Show data in browser. */
	
	//var data = getData();
	var result = getData();
	aHead = result[0];
	aData = result[1];
	console.log('aData:', aData);
	if (!aData) {
		return
	}

	drawTable(aData, aHead);
}


function getData() {
	/* Get Tracker's data from server. */
	
	var params = getRequestParams(true);
	if (!params) {
		return false;
	}
	console.log('params:', params);

	var result = JSON.parse(httpRequest('getdata?' + params)); //, 'POST'
	console.log('result:', result);
	if (!result) {
		alert('Cannot get data.');
		return false;
	} else {
		return result;
	}
}


function drawTable(data, heads) {
	// Show Tracker's data as a table.
	
	// Remove table if exists
	var tblData = document.getElementById("tblData");
	if (tblData) {
		tblData.remove();
	}

	// Create table
	tblData = document.createElement('table');
	document.getElementById('divTable').appendChild(tblData);
	tblData.setAttribute("id", "tblData");
	tblData.setAttribute("class", "table table-striped table-hover table-bordered ");
	// Create table header
	var tHead = tblData.createTHead();
    var headerRow = tHead.insertRow(0);
	var th = document.createElement("th");
	th.innerHTML = "No";
	headerRow.appendChild(th);
	for (let i = 0; i < heads.length; i++) {
		th = document.createElement("th");
		th.innerHTML = heads[i];
		th.onclick = function() {
			sortTable(i);
		}
		headerRow.appendChild(th);
	}
	// Create table body
	var tBody = document.createElement('tbody');
	tblData.appendChild(tBody);
	// Show data in table
	var i = 0;
	for (var row of data) {
		//console.log('row:', row);
		i += 1;
		var tr = document.createElement('tr');
		var td = document.createElement('td');
		td.innerHTML = i;
		td.setAttribute("class", "text-end");
		tr.appendChild(td);
		
		for (var text of row) {
			var td = document.createElement('td');
			td.innerHTML = text;
			tr.appendChild(td);
			if(typeof text === 'number') {
				td.setAttribute("class", "text-end");
			}
		}
		tBody.appendChild(tr);
	}
}


function sortTable(colNum) {
	/* Sort table content by column. */

	// console.log('colNum:', colNum);
	// Sort table data
	aData = aData.sort(function(a, b) {
		return a[colNum] > b[colNum] ? 1 : -1;
	})
	drawTable(aData, aHead);
}


function updateData() {
	/*
	Sent parameters for updating data in database and display result.
	*/

	var params = getRequestParams(true);
	if (!params) {
		return false;
	}
	// console.log('params:', params);

	var result = JSON.parse(httpRequest('update?' + params));  //, 'POST'
	//console.log('Update result:', result);
	if (result) {
		alert('Update OK: ' + result + ' rows.');
	} else {
		alert('Update failed.');
	};
}


function getRequestParams(check) {
	/*
	Generates and returns parameters for http request.
	*/

	var params = {};
	var periodsObj = document.getElementById("periods").children;
	var periods = []
	var periodIsEmpty = false;
	for (let i = 0; i < periodsObj.length; i++) {
		if (!periodsObj[i].querySelector('#date_start').value ||
			!periodsObj[i].querySelector('#date_end').value) {
			periodIsEmpty = true;
			break;
		};
		periods.push({
			date_start: periodsObj[i].querySelector('#date_start').value,
			date_end: periodsObj[i].querySelector('#date_end').value
		});
	}
	if (periodIsEmpty) {
		alert('The Period field values must not be empty!');
		return false;
	}
	params = 'periods=' + JSON.stringify(periods);
	//console.log('params:', params);
	return params;
}


function httpRequest(url, reqType='GET', asyncProc=false) {
	//var req = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
	var req = new XMLHttpRequest();
	if (asyncProc) { 
		req.onreadystatechange = function() { 
		  if (this.readyState == 4) {
		    asyncProc(this);
		  } 
		}
	} else { 
	  //req.timeout = 4000;  // Reduce default 2mn-like timeout to 4 s if synchronous
	}
	req.open(reqType, url, asyncProc);
	req.send();
	if (req.status === 200 ) {
		return req.response;
	} else {
		return false;
	}
}

