document.addEventListener("DOMContentLoaded", function(){

const help=document.createElement("div")

help.style.position="fixed"
help.style.bottom="20px"
help.style.right="20px"
help.style.background="#4a5cff"
help.style.color="white"
help.style.padding="14px"
help.style.borderRadius="10px"
help.style.cursor="pointer"
help.style.zIndex="999"

help.innerText="AI Help"

help.onclick=function(){

alert(
"Upload a lesson PDF and the system will automatically generate worksheets, quizzes, and answer keys."
)

}

document.body.appendChild(help)

})