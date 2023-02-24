// Поучаю service_id из адреса сайта
const service_id = window.location.pathname.split('/')[1]
// Делаем кнопку неактивной
const elementButton = document.querySelector('#submit')
elementButton.disabled = true

function createListTime(obj) {
	// console.log(obj);
	// for (time of obj) {
	// 	console.log((new Date(time)).toLocaleTimeString().slice(0, -3));
	// }
	arr = []
	for (time of obj) {
		arr.push({'label': (new Date(time)).toLocaleTimeString().slice(0, -3), 'value': time})
	}
	console.log(arr);
	const elementList = document.querySelector('#time')
	elementList.innerHTML = `
	<input type="radio" id="contactChoice1" name="contact" value="email">
	<label for="contactChoice1">Email</label>

	<input type="radio" id="contactChoice2" name="contact" value="phone">
	<label for="contactChoice2">Phone</label>`
}

new AirDatepicker('#datepicker', {
	isMobile: true,
	autoClose: true,
	minDate: new Date(),
	maxDate: (new Date()).setDate(new Date().getDate() + 7),
	onSelect({ formattedDate }) {
		if (formattedDate) {
			fetch("/getting_time", {
				method: 'POST',
				body: JSON.stringify({ date: formattedDate, service_id: service_id })
			})
				.then(response => {
					if (!response.ok) {
						throw new Error('Нет связи с сервером')
					}
					return response.json()
				}).then(responseJson => {
					createListTime(responseJson['time'])
				}).catch((error) => {
					console.log(error)
				})
		}
	}
})