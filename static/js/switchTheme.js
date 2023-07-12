document.getElementById('lightMode').addEventListener('click',()=>{
    document.documentElement.setAttribute('data-bs-theme','light')
})

document.getElementById('darkMode').addEventListener('click',()=>{
    document.documentElement.setAttribute('data-bs-theme','dark')
})

document.getElementById('autoMode').addEventListener('click',()=>{
    document.documentElement.setAttribute('data-bs-theme','auto')
})