/**
 * Изменяем значений времени всех полей в списке к времени UTC
 * @param {Array} elements Список элементов, значение которых подлежит конвертации
 */
function fromLocalToUtc(elements) {
	elements.forEach(function (item) {
		let list_time = item.value.split(':');
		let hour = list_time[0];
		let minute = list_time[1];
		item.value = moment().set({ 'hour': hour, 'minute': minute }).utc().format('HH:mm');
	});
}
// Во время обработки формы происходит перевод времени в UTC
let form = document.querySelector("form");
form.addEventListener("submit", function (event) {
	fromLocalToUtc([document.getElementById('begin_of_the_day'), document.getElementById('end_of_the_day')])
	console.log([document.getElementById('begin_of_the_day'), document.getElementById('end_of_the_day')]);
});