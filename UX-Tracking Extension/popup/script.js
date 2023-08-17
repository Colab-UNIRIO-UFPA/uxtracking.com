document.addEventListener('DOMContentLoaded', () => {
  var formLogin = $('#formLogin');

  formLogin.submit(function (e) {
    e.preventDefault();
    const username = $("#username").val();
    const password = $("#password").val();

    $.post("http://192.168.100.41:5000/userAuth",
    {
      username: username,
      password: password
    },
    function(authToken){
      chrome.storage.sync.set({ "authToken": authToken.id }, function(){
        console.log("User Authenticated!");
      });
      document.getElementById("divLogin").style.display = "none";
      document.getElementById("mainContent").style.display = "";
    });
  });

  const links = document.querySelectorAll("a");

  links.forEach(link => {
    const location = link.getAttribute('href');
    link.addEventListener('click', () => chrome.tabs.create({active: true, url: location}));
  });
});

function setKey(e, key) {
  let target = e.target.checked

  browser.storage.local.set({ [key]: target }).catch((e) => {
    console.error(e)
  })
}

function getKey(id, key) {
  browser.storage.local.get([key]).then((result) => {
    let target = result[key]

    document.getElementById(id).checked = !!target
  })
}

getKey('__listen_mouse__', 'mouse')
getKey('__listen_keyboard__', 'keyboard')
getKey('__listen_microphone__', 'microphone')
getKey('__listen_camera__', 'camera')

document.getElementById('__listen_mouse__').addEventListener('change', (e) => {
  setKey(e, 'mouse')
})

document
  .getElementById('__listen_keyboard__')
  .addEventListener('change', (e) => {
    setKey(e, 'keyboard')
  })

document
  .getElementById('__listen_microphone__')
  .addEventListener('change', (e) => {
    setKey(e, 'microphone')
  })

document.getElementById('__listen_camera__').addEventListener('change', (e) => {
  setKey(e, 'camera')
})
