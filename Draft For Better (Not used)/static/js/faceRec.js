const enterPass = document.getElementById('enterPass');
const face = document.getElementById('face');
const newPass = document.getElementById('newPass');
const validpass = document.getElementById('validPass');
const changePass = document.getElementById('changePass');
const change = document.getElementById('change');
const cancel = document.getElementById('cancel');
const webcam = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
let head=document.getElementsByClassName('head')[0];
let faceRec=document.getElementsByClassName('faceRec')[0];
const addUserBtn = document.getElementById('addUserBtn');  
const addUserDiv = document.getElementById('addUser');  
const submitUserBtn = document.getElementById('submitUser');  
const cancelUser = document.getElementById('cancelUser'); 
const userNameInput = document.getElementById('userName');  
const userImageInput = document.getElementById('userImage'); 
let storedPassword = JSON.parse(localStorage.getItem('password')) || '1234';
const deleteUserBtn = document.getElementById('deleteUserBtn');
const deleteUserDiv = document.getElementById('deleteUserDiv');
const confirmDelete = document.getElementById('confirmDelete');
const cancelDelete = document.getElementById('cancelDelete');
const deleteUserNameInput = document.getElementById('deleteUserName');
let truepass=false;
const menubtn = document.getElementById('menubtn');
const menu = document.getElementById('menu');
const passwordValue ="";
let menupass=document.getElementById('menupass');
let temp = "face";
let capturedImage = ""; 
let captureActive = false;  

let st;
let personName;
function startWebcam() {
    console.log('Camera is open');
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            st = stream;
            webcam.srcObject = stream;
            webcam.style.display = 'block';
            captureActive = true; 
            startFrameCapture();
        })
        .catch((error) => {
            console.error('Error accessing the webcam:', error);
        });
}

// Stop the webcam and clear the capture interval
function stopWebcam() {
    if (st) {
        temp="stop";
        st.getTracks().forEach(track => track.stop());
        webcam.srcObject = null;
        webcam.style.display = 'none';
        context.clearRect(0, 0, canvas.width, canvas.height);
    }
    clearInterval(captureInterval);
    captureActive = false;  // Set flag to false when webcam stops
}
function adjustCanvasSize() {
    canvas.width = webcam.videoWidth;
    canvas.height = webcam.videoHeight;
}
webcam.addEventListener('loadedmetadata', adjustCanvasSize);
function startFrameCapture() {
    captureInterval = setInterval(() => {
        if (webcam.srcObject) {
            captureAndSendImage();
        }
    }, 1);  

} 
function captureAndSendImage() {
    if (!captureActive) return;  // Don't proceed if capture is stopped
    context.drawImage(webcam, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL("image/png");
    capturedImage = dataURL;
  
    fetch('/recognize_face', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: dataURL })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (!captureActive) return;
        console.log('Response Data:', data);  
        personName = data.name;
        console.log('Detected Name:', personName);
        let color = (personName !== 'Unknown') ? 'green' : 'red';
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(webcam, 0, 0, canvas.width, canvas.height);
        if (data.face_locations.length > 0) {
     

            console.log('Face Locations:', data.face_locations);
            data.face_locations.forEach(location => {
                const [top, right, bottom, left] = location;
                console.log(`Drawing rectangle: top=${top}, right=${right}, bottom=${bottom}, left=${left}`);
                context.strokeStyle = color;
                context.lineWidth = 2;
                context.strokeRect(left, top, right - left, bottom - top);
            
            });
     
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
    if(personName === 'Unknown') {
        head.innerHTML = `<h3>Your face has been sent to the homeowners. Please wait for a response...</h3>`;
       
            fetch('/homeRes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: dataURL })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Response from server:', data);
            
            })
            .catch(error => {
                console.error('Error:', error);
            });
        

    }
}

function validPass(value) {
    let tries = JSON.parse(sessionStorage.getItem('tryPass')) || 5;
    const storedPassword = JSON.parse(localStorage.getItem('password')) || '1234';  // Example stored password
    if (value.length === storedPassword.length) {
    // Compare the entered password with the stored one
    if (value === storedPassword) {
        truepass=true;
        enterPass.disabled = true;
        enterPass.style.background = 'green';
        validpass.style.color = 'green';
        validpass.innerText = 'Correct password';

        setTimeout(() => {
            enterPass.disabled = false;
            
        }, 1000);

   
    } else {
        tries--;
        sessionStorage.setItem('tryPass', JSON.stringify(tries));
        enterPass.style.background = 'red';
        validpass.style.color = 'red';
        validpass.innerText = 'Wrong password!!';

        if (tries <= 0) {
            validpass.innerText = 'Wait 30 secs to try again';
            enterPass.disabled = true;
            setTimeout(() => {
                enterPass.disabled = false;
                sessionStorage.setItem('tryPass', JSON.stringify(5));
                location.reload();
            }, 30000);
        } else {
            setTimeout(() => {
                enterPass.disabled = false;
            }, 1000);
        }

      
    }
}
}


/////delete user
deleteUserBtn.addEventListener('click', () => {
    deleteUserDiv.classList.remove('hide');
    change.classList.add('hide');
    addUserDiv.classList.add('hide');
   
});
cancelDelete.addEventListener('click', () => {
    deleteUserDiv.classList.add('hide');
});
confirmDelete.addEventListener('click', () => {
    deleteUser();
});
function deleteUser() {
    const name = deleteUserNameInput.value;

    if (!name) {
        alert('Please enter a name.');
        return;
    }

    fetch('/delete_user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
           deleteUserNameInput.value='';
            deleteUserDiv.classList.add('hide');
        
    })
    .catch(error => {
        console.error('Error deleting user:', error);
      
    });
}
// Event listeners
enterPass.addEventListener('input', () => validPass(enterPass.value));


face.onclick = function () {
   
    faceRec.style.display='block';
    if (temp === "face") {
        startWebcam();
        temp = "stop";
        face.value ="Capyture and send";
    } else {
        stopWebcam();
        temp = "face";
        face.value = "Start Camera";
    }
};
////change pass
changePass.addEventListener('click', () => {
    //startWebcam();
    change.classList.remove('hide');
    deleteUserDiv.classList.add('hide');
    addUserDiv.classList.add('hide');
   
    
});

// Function to confirm and change password
document.getElementById('confirm').addEventListener('click', () => {
    
    const newPassValue = newPass.value; // Get new password

        // If correct, proceed to change the password
        fetch('/change_password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_password: newPassValue })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Password change status:', data.status);
            if (data.status === 'Password updated') {
                console.log('Password changed successfully!');
                // Store the new password locally
                localStorage.setItem('password', JSON.stringify(newPassValue));
                // Reset the form
                change.classList.add('hide');
                newPass.value = '';

            } else {
                alert('Failed to change password. Try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
   
 
});
let clickCount = 0;

// Event listener for menu button click
menubtn.onclick = function () {
    clickCount++;
    if(clickCount % 2 === 0){
        menupass.classList.add('hide');
        menu.classList.add('hide');
        faceRec.classList.remove('hide');
    }
    else{
        faceRec.classList.add('hide');
        menupass.classList.remove('hide');
        menupass.onkeyup=function(){
           if(this.value.length===storedPassword.length){
             if(this.value===storedPassword){
              
                 menu.classList.remove('hide');
                 menupass.classList.add('hide');
             }
          
             this.value='';
           }
        }
         
    }
 
};


cancel.addEventListener('click', () => {
    change.classList.add('hide');
    newPass.value = '';
   
});
addUserBtn.addEventListener('click', () => {
    change.classList.add('hide');
    deleteUserDiv.classList.add('hide');
    addUserDiv.classList.remove('hide');

});

///adding new user
submitUserBtn.addEventListener('click', async () => {
    let name = userNameInput.value;
    let file = userImageInput.files[0];

    if (!name || !file) {
        alert('Please provide both name and image.');
        return;
    }

    let formData = new FormData();
    formData.append('name', name);
    formData.append('img', file);

    try {
        const response = await fetch('/add_user', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Success:', data);
        } else {
            //console.error('Error:', response.statusText);
        }
    } catch (error) {
        console.error('Fetch error:', error);
    }
});


document.getElementById('cancelUser').addEventListener('click', () => {
    addUserDiv.classList.add('hide');
   
});
enterPass.onkeyup=function(){
    if(this.value.length=== storedPassword.length){
        passwordValue=this.value;
        validPass(this.value);
    }
 


}
async function convertToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}
