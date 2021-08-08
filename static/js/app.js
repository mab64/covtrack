'use strict';

var cnt = 1;

var groupbyValue = '0';
// var groupbyElement;

var chartData;

window.onload = function() {
	// Setup the GO button click handler.
	document.getElementById("btnGo").onclick = function() {
		if (document.getElementById('op_type1').checked) {
			var route = 'table';
		} else {
			updateData();
		};
	};
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
    };
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
		console.log('Update result:', result);
	} else {
		console.log('Update failed.');
	};
}


function appendPeriod(obj) {
	// <!-- var obj = document.getElementById("period1"); -->
	var parentObj = document.getElementById("periods");
	var newObj = parentObj.appendChild(obj.cloneNode(true));
	<!-- var newObj = document.createElement('div'); -->
	cnt += 1;
	var periodId = "period" + cnt;
	newObj.setAttribute("id", periodId);
	<!-- parentObj.appendChild(newObj); -->
	<!-- newObj.getElementById("btnAdd").innerHTML = " - "; -->
	
	newObj.querySelector("#btnAdd").setAttribute('value', ' - ');
	newObj.querySelector("#btnAdd").setAttribute("onclick", 
			"removePeriod(this.parentNode); return false;");
	newObj.querySelector("#date_start").setAttribute("name", "date_start_" + cnt);
	newObj.querySelector("#date_end").setAttribute("name", "date_end_" + cnt);
	
	// console.log(newObj.id);
	// console.log(parentObj.children.length);
}

function removePeriod(obj) {
	obj.parentNode.removeChild(obj);
	// cnt -= 1;
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

