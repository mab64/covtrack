'use strict';

var cnt = 1;
var aData = [];

var groupbyValue = '0';
// var groupbyElement;

var chartData;

window.onload = function() {
	// Setup the GO button click handler.
	document.getElementById("btnGo").onclick = function() {
		if (document.getElementById('op_type1').checked) {
			showData();
		} else {
			updateData();
		}
	}
	// 
	var groupbyElement = document.getElementById('group_by');
	groupbyElement.addEventListener('change', function() {
		groupbyValue = groupbyElement.selectedIndex;
		// console.log(groupbyValue);
	})

}

function sendData(route) {
	var params = '';

	var periodsObj = document.getElementById("periods").children;
	for (let i = 0; i < periodsObj.length; i++) {
		// console.log('Obj: ', periodsObj[i]);
		params += '&date_start_' + (i+1) + '=' + 
					periodsObj[i].querySelector('#date_start').value;
		params += '&date_end_' + (i+1) + '=' + 
					periodsObj[i].querySelector('#date_end').value;
		
	}
	//console.log(params);
	var xhr = new XMLHttpRequest();
	xhr.open('GET', route + '?' + params);
	xhr.onload = function() {
		if (xhr.status === 200) {
			var result = JSON.parse(xhr.responseText);
			console.log('sendData result:', result);
			return result;
		} else {
			alert('Request failed.  Returned status: ' + xhr.status);
			return false;
		}
	};
	xhr.send();
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


function drawTable(data, heads) {
	// Show Tracker's data in table.
	
	console.log('Head:', heads);

	var tblData = document.getElementById("tblData");
	if (tblData) {
		tblData.remove();
	}
	tblData = document.createElement('table');
	document.getElementById('divTable').appendChild(tblData);
	tblData.setAttribute("id", "tblData");
	tblData.setAttribute("class", "table table-striped table-hover table-bordered");
	
	// var tHead = document.createElement('thead');
	// tblData.appendChild(tHead);
 	// var tr = document.createElement('tr');
	// tHead.appendChild(tr);
	// for (var head of heads) {
	// 	var td = document.createElement('td');
	// 	td.appendChild(document.createTextNode(head));
	// 	tr.appendChild(td);
	// }
		
	var tHead = tblData.createTHead();
    var headerRow = tHead.insertRow(0);
	for (var head of heads) {
		var th = document.createElement("th");
		th.innerHTML = head;
		headerRow.appendChild(th);
	}
	

	var tBody = document.createElement('tbody');
	tblData.appendChild(tBody);
	var i = 0;
	for (var row of data) {
		//console.log('row:', row);
		i += 1;
		var tr = document.createElement('tr');
		var td = document.createElement('td');
		td.innerHTML = i;
		tr.appendChild(td);
		
		// var j = 1;
		for (var text of row) {
			var td = document.createElement('td');
			// td.appendChild(document.createTextNode(text));
			td.innerHTML = text;
			//i == 1 && j == 1 ? td.setAttribute('rowSpan', '2') : null;
			tr.appendChild(td);
			// td.setAttribute("class", "text-end");
		}
		tBody.appendChild(tr);
	}
}


function showData() {
	// Show data in browser.
	
	//var data = getData();
	aData = getData();
	console.log('aData:', aData);
	if (!aData) {
		return
	}

	var head = ['NN', 'Country', 'Confirmed', 'Deaths', 'String. Actual', 'Stringency'];
	drawTable(aData, head);
	
}


function getData() {
	// Get Tracker's data from server.
	
	var params = getRequestParams(true);
	if (!params) {
		return false;
	}
	console.log('params:', params);

	var data = JSON.parse(httpRequest('getdata?' + params, 'POST'));
	//console.log('Update result:', result);
	if (!data) {
		alert('Cannot get data.');
		return false;
	} else {
		return data;
	}
}

function updateData() {
	//params += '&qty_time=';
	var params = getRequestParams(true);
	if (!params) {
		return false;
	}
	console.log('params:', params);

	var result = JSON.parse(httpRequest('update?' + params, 'POST'));
	//console.log('Update result:', result);
	if (result) {
		alert('Update OK: ' + result + ' rows.');
	} else {
		alert('Update failed.');
	};
}


function getRequestParams(check) {
	//
	// Returns all parameters for http request.
	//
	var params = {};
	// params.screenName = document.getElementById("screen_name").value;
	var periodsObj = document.getElementById("periods").children;
	var periods = []
	var periodIsEmpty = false;
	for (let i = 0; i < periodsObj.length; i++) {
		// console.log('Obj: ', periodsObj[i]);
		if (!periodsObj[i].querySelector('#date_start').value ||
			!periodsObj[i].querySelector('#date_end').value) {
			periodIsEmpty = true;
			break;
		};

		//arams += 'date_start_' + (i+1) + '=' + 
		//		periodsObj[i].querySelector('#date_start').value + '&';
		//params += 'date_end_' + (i+1) + '=' + 
		//		periodsObj[i].querySelector('#date_end').value + '&';
		
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

