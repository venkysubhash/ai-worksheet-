function toggleTheme(){

const body=document.body

if(body.classList.contains("dark")){
body.classList.remove("dark")
localStorage.setItem("theme","light")
}
else{
body.classList.add("dark")
localStorage.setItem("theme","dark")
}

}

document.addEventListener("DOMContentLoaded",function(){

if(localStorage.getItem("theme")==="dark"){
document.body.classList.add("dark")
}

})