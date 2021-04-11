const status = document.getElementById('cardStatus')
const sendStatus = document.getElementById('sendStatus')
const sendStatus2 = document.getElementById('sendStatus2')

if (status) {
    status.addEventListener('change', () => {
        console.log('im in')
        if (status.checked) {
            sendStatus.value = "MASTERED"
            sendStatus2.value = "MASTERED"
        } else {
            sendStatus.value = "LEARNING"
            sendStatus2.value = "LEARNING"
        }
    })
}

