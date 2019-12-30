PAD_ID = -1;
gamepads = [];

function supportsGamepads() {
	return !!(navigator.getGamepads);
}

last_press = new Date().getTime();

function httpGet(theUrl) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
    xmlHttp.send( null );
    return xmlHttp.responseText;
}

function checkAvailable (argument) {
	if (supportsGamepads()) {
		// Get the state of all gamepads
		gamepads = navigator.getGamepads();


		table_start = "<table><tr> <th>ID</th> <th>Name</th> <th></th> </tr>";
		table_end = "</table>";
		row = "<tr> <td>{{ID}}</td> <td>{{NAME}}</td> <td><button onclick='selectGamepad({{ID}});'>Select</button></td> </tr>";

		for (let i = 0; i < gamepads.length; i++) {
		    console.log("Gamepad " + i + ":");

		    if (gamepads[i] === null) {
		        console.log("[null]");
		        continue;
		    }

		    if (!gamepads[i].connected) {
		        console.log("[disconnected]");
		        continue;
		    }

		    console.log("    Index: " + gamepads[i].index);
		    console.log("    ID: " + gamepads[i].id);
		    console.log("    Axes: " + gamepads[i].axes.length);
		    console.log("    Buttons: " + gamepads[i].buttons.length);
		    console.log("    Mapping: " + gamepads[i].mapping);

		    table_start += row.replace("{{ID}}", gamepads[i].index).replace("{{NAME}}", gamepads[i].id).replace("{{ID}}", gamepads[i].index)
		}
		table_start += table_end;
		document.getElementById("gamepads_table").innerHTML = table_start;
	} else {
		// TODO Elaborate on how to debug
		alert("supportsGamepads : false");
	}
}

function selectGamepad(id) {
	PAD_ID = id;

	$('<div></div>').html(gamepads[PAD_ID].id).dialog({
		title: 'Selected Gamepad',
		buttons: {
            'Ok': function()  {
                $( this ).dialog( 'close' );
            }
        }
	});

	$( "#gamepads_table_dialog" ).dialog('close');

	// Kick off the rendering
	requestAnimationFrame(handleFrame);
}

function auto_refresh () {
	if (PAD_ID == -1) {
		checkAvailable();
		setTimeout(auto_refresh, 1000);
	}
}

$( function() {
    $( "#gamepads_table_dialog" ).dialog();
	auto_refresh();
});


// Handle controls and drawing a new frame
STEER_ID = -1;
ACCEL_ID = -1;
SPEED_ID = [-1, -1];
function controlChange (context, id, ad) {
	console.log(context.selectedIndex);
	console.log(id);
	if (ad == 'analog') {
		if (context.selectedIndex==1) {
			ACCEL_ID = id;
		} else if (context.selectedIndex==2) {
			STEER_ID = id;
		}
	} else {
		SPEED_ID[context.selectedIndex-1] = id;
	}
}

ANALOG_INVERT = [];
DIGITAL_INVERT = [];
function invertChange (context) {
	id = Number(context.name);
	console.log(context);
	console.log(id);

	if (ANALOG_INVERT==[]) {
		for (i=0; i<gamepads[PAD_ID].axes; i++) {
			ANALOG_INVERT.append(false);
		}
	}

	if (DIGITAL_INVERT==[]) {
		for (i=0; i<gamepads[PAD_ID].buttons; i++) {
			DIGITAL_INVERT.append(false);
		}
	}

	if (context.value == 'analog') {
		ANALOG_INVERT[id] = context.checked;
	} else {
		DIGITAL_INVERT[id] = context.checked;
	}
}

function handleFrame(timestamp) {

	gamepads = navigator.getGamepads();

	analog_table = document.getElementById('analog_table');
	digital_table = document.getElementById('digital_table');

	if (analog_table == null || digital_table == null) {
		analog_drop_down = '<select onchange="' + "controlChange(this, {{ID}}, 'analog');" + '" name="analog_drop_down"><option value="none">Select</option><option value="front_back">Front-Back</option><option value="left_right">Left Right</option></select>';
		digital_drop_down = '<select onchange="' + "controlChange(this, {{ID}}, 'digital');" + '" name="digital_drop_down"><option value="none">Select</option><option value="speed_up">Speed Up</option><option value="speed_down">Slow Down</option></select>';

		table_start = "<h1>{{GAMEPAD_NAME}}</h1><h2>Analog</h2><table id='analog_table'><tr> <th>ID</th> <th>Name</th> <th>Use</th> <th>Invert</th> </tr>";
		table_end = "</table>";
		row = "<tr> <td>{{ID}}</td> <td>{{MAG}}</td> <td>" + analog_drop_down + "</td> <td><input onchange='invertChange(this);' type='checkbox' name='{{ID}}' value='analog'></td> </tr>";

		table_start = table_start.replace('{{GAMEPAD_NAME}}', gamepads[PAD_ID].id);

		axes = gamepads[PAD_ID].axes;
		for (let i=0; i<axes.length; i++) {
			table_start += row.replace('{{ID}}', i).replace('{{MAG}}', Math.floor(axes[i].toFixed(2)*100) + " %").replace('{{ID}}', i).replace('{{ID}}', i);
		}
		table_start += table_end;

		res = table_start;

		table_start = "<h2>Digital</h2><table id='digital_table'><tr> <th>ID</th> <th>Name</th> <th>Use</th> <th>Invert</th> </tr>";
		row = "<tr> <td>{{ID}}</td> <td>{{MAG}}</td> <td>" + digital_drop_down + "</td><td><input onchange='invertChange(this);' type='checkbox' name='{{ID}}' value='digital'></td> </tr>";
		buttons = gamepads[PAD_ID].buttons;
		for (let i=0; i<buttons.length; i++) {
			table_start += row.replace('{{ID}}', i).replace('{{MAG}}', buttons[i].pressed).replace('{{ID}}', i);
		}

		res += table_start;

		document.getElementById('gamepad_data').innerHTML = res;
	} else {
		axes = gamepads[PAD_ID].axes;
		for (let i=0; i<axes.length; i++) {
			let analog_cell = analog_table.rows[i+1].cells[1];
			if (analog_cell.innerHTML != Math.floor(axes[i].toFixed(2)*100) + " %") {
				analog_cell.style.background = "green";
				setTimeout(function () {
					analog_cell.style.background = "white";
				}, 500);
			}
			analog_cell.innerHTML = Math.floor(axes[i].toFixed(2)*100) + " %";
		}

		buttons = gamepads[PAD_ID].buttons;
		for (let i=0; i<buttons.length; i++) {
			let digital_cell = digital_table.rows[i+1].cells[1];
			if (digital_cell.innerHTML != String(buttons[i].pressed)) {
				digital_cell.style.background = "green";
				setTimeout(function () {
					digital_cell.style.background = "white";
				}, 500);
			}
			digital_cell.innerHTML = buttons[i].pressed;
		}
	}

	if (STEER_ID!=-1) {
		steering_wheel = document.getElementById('steering_wheel');

		invert = 1;
		if (ANALOG_INVERT[STEER_ID])
			invert = -1;

	    steering_wheel.style.transform = 'rotate(' + gamepads[PAD_ID].axes[STEER_ID] * 90 * 1.5 * invert + 'deg)';

	    steering_angle = document.getElementById('steering_angle');
	    steering_angle.innerHTML = Math.floor(gamepads[PAD_ID].axes[STEER_ID] * 45) + " degrees";
	}

	if (ACCEL_ID!=-1) {
		steering_wheel = document.getElementById('steering_wheel');
		
		invert = 1;
		if (ANALOG_INVERT[ACCEL_ID])
			invert = -1;
	    

	    val = Math.floor(gamepads[PAD_ID].axes[ACCEL_ID].toFixed(4)*100) * invert;

	    accel_val = document.getElementById('accel_val');
	    accel_type = document.getElementById('accel_type');
	    accel_val.innerHTML = val + " %";
	    if (val>0) {
	    	accel_type.innerHTML = "Accelerating";
	    	accel_val.style.background = "green";
	    } else if (val<0) {
			accel_type.innerHTML = "Deccelerating";
			accel_val.style.background = "red";
	    } else {
	    	accel_type.innerHTML = "-";
	    }

	    setTimeout(function () {
	    	accel_val.style.background = "white";
	    }, 1500);
	}

	current_speed = document.getElementById('current_speed');
	now = new Date().getTime();

	if (SPEED_ID[0]!=-1) {
		speed_up = document.getElementById('speed_up');
		if (gamepads[PAD_ID].buttons[SPEED_ID[0]].pressed) {
			speed_up.style.background = "green";
			if (Number(current_speed.innerHTML)<4 && now-last_press>250 ) {
				current_speed.innerHTML = Number(current_speed.innerHTML)+1;
				last_press = now;
			}
			setTimeout(function (argument) {
				speed_up.style.background = "white";
			}, 1500);
		}
	}

	if (SPEED_ID[1]!=-1) {
		slow_down = document.getElementById('slow_down');
		if (gamepads[PAD_ID].buttons[SPEED_ID[1]].pressed) {
			slow_down.style.background = "green";
			if (Number(current_speed.innerHTML)>1 && now-last_press>250 ) {
				current_speed.innerHTML = Number(current_speed.innerHTML)-1;
				last_press = now;
			}
			setTimeout(function (argument) {
				slow_down.style.background = "white";
			}, 1500);
		}
	}

    // Render it again
    requestAnimationFrame(handleFrame);
}
