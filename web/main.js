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

}

// Kick off the rendering
requestAnimationFrame(handleFrame);

function auto_refresh() {
	if (PAD_ID == -1) {
		checkAvailable();
		setTimeout(auto_refresh, 1000);
	}
}

function select_gamepad_dialog() {
	$( "#gamepads_table_dialog" ).dialog();
	auto_refresh();
}


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

steering_angle = 0
accel_val = 0
rec = 0
message = "/?steering_angle={{steering_angle}}&accel_val={{accel_val}}&rec={{rec}}"
last_message = ""
last_keypress = new Date().getTime()
document.onkeypress = function (e) {
    e = e || window.event;
    steering_angle = 0
	accel_val = 0
	last_keypress = new Date().getTime()
    switch(e.key) {
    	case "w":
    		accel_val = 100;
    		break;
    	case "s":
    		accel_val = -100;
    		break;
    	case "d":
    		steering_angle = 1;
    		break;
    	case "a":
    		steering_angle = -1;
    		break;
    	case "p":
    		current_speed = document.getElementById('current_speed');
    		if (Number(current_speed.innerHTML)<4) {
				current_speed.innerHTML = Number(current_speed.innerHTML)+1;
			}
			break;
		case "o":
			current_speed = document.getElementById('current_speed');
    		if (Number(current_speed.innerHTML)>1) {
				current_speed.innerHTML = Number(current_speed.innerHTML)-1;
			}
    }
};

function handleFrame(timestamp) {

	gamepads = navigator.getGamepads();

	analog_table = document.getElementById('analog_table');
	digital_table = document.getElementById('digital_table');

	if (PAD_ID!=-1 && gamepads[PAD_ID]!=undefined) {
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
	}

	if (STEER_ID!=-1) {

		invert = 1;
		if (ANALOG_INVERT[STEER_ID])
			invert = -1;


        steering_angle = gamepads[PAD_ID].axes[STEER_ID] * invert;
	}
	steering_wheel = document.getElementById('steering_wheel');
    steering_wheel.style.transform = 'rotate(' + steering_angle * 90 * 1.5  + 'deg)';
	steering_angle_ele = document.getElementById('steering_angle');
	steering_angle_ele.innerHTML = Math.floor(steering_angle * 45) + " degrees";

	if (ACCEL_ID!=-1) {
		steering_wheel = document.getElementById('steering_wheel');
		
		invert = 1;
		if (ANALOG_INVERT[ACCEL_ID])
			invert = -1;
	    
	    accel_val = Math.floor(gamepads[PAD_ID].axes[ACCEL_ID].toFixed(4)*100) * invert;
	}

	accel = document.getElementById('accel_val');
	accel_type = document.getElementById('accel_type');
	accel.innerHTML = accel_val + " %";
	if (accel_val>0) {
	    accel_type.innerHTML = "Accelerating";
	    accel.style.background = "green";
	} else if (accel_val<0) {
		accel_type.innerHTML = "Deccelerating";
		accel.style.background = "red";
	} else {
		accel_type.innerHTML = "-";
	}

	setTimeout(function () {
		accel.style.background = "white";
	}, 1500);

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

    m = message.replace("{{steering_angle}}", steering_angle).replace("{{accel_val}}", accel_val).replace("{{rec}}", rec)
    if (m != last_message) {
        res = httpGet(document.location.origin + m)
		//console.log(res)
        last_message = m
    }

   	now = new Date().getTime();
    if (now - last_keypress>100) {
    	steering_angle = 0
		accel_val = 0
    }

	// Render it again
    requestAnimationFrame(handleFrame);
}

function start_recording() {
	record_button = document.getElementById('record_button')
	recording_name = document.getElementById('recording_name')
	if (recording_name.value != "") {
		if (rec == 0 ) {
			rec = recording_name.value
			record_button.innerHTML = "Stop Recording"
			record_button.style.background = "grey"
		} else {
			rec = 0
			record_button.innerHTML = "Start Recording"
			record_button.style.background = "red"
		}
	} else {
		$('<div></div>').html('Recording name can not be black').dialog({
			title: "Recording Name",
			buttons: {
	            'Ok': function()  {
	                $( this ).dialog( 'close' );
	            }
	        }
		});
	}
}

$(function() {
        $.contextMenu({
            selector: '.card', 
            callback: function(key, options) {
                console.log(key); 
                console.log($(this).text())
            },
            items: {
                "download": {name: "Download", icon: "fa-download"},
                "rename": {name: "Rename", icon: "fa-edit"},
                "delete": {name: "Delete", icon: "fa-trash"}
            }
        });

        $('.card').on('click', function(e){
            console.log(this);
        })    
    });
