"use strict";

document.addEventListener("DOMContentLoaded", () => {
	// Получаем service_id из адреса сайта
	const service_id = window.location.pathname.split("/")[2];
	const elementStatus = document.querySelector("#statusTime");
	const elementTime = document.querySelector("#listTime");
	const calendarElement = document.querySelector("#datepicker");
	const btnSubmit = document.querySelector("#submit");
	btnSubmit.disabled = true;
	// Маскимальная дата ограничена настройками пользователя
	const amount_of_days = calendarElement.dataset.amount_of_days;
	const maxDate = new Date().setDate(new Date().getDate() + amount_of_days);
	const url = calendarElement.dataset.url;

	new AirDatepicker("#datepicker", {
		isMobile: true,
		autoClose: true,
		minDate: new Date(),
		maxDate: maxDate,
		dateFormat: "yyyy-MM-dd",
		onSelect({ formattedDate }) {
			if (formattedDate) changeListTime(formattedDate);
		},
	});

	async function changeListTime(date) {
		try {
			btnSubmit.disabled = true;
			elementTime.innerHTML = "";
			// Делаем запрос
			document.querySelector(".form-box").classList.add("_sending");
			const response = await fetch(url, {
				method: "POST",
				body: JSON.stringify({ date: date, service_id: service_id }),
			});
			if (!response.ok) throw new Error();
			// Получаем данные из ответа
			const json = await response.json();
			updateElements(json.time);
			document.querySelector(".form-box").classList.remove("_sending");
		} catch (error) {
			elementStatus.textContent = "Ошибка соединения с сервером";
		}
	}

	function updateElements(listTime) {
		if (listTime.length == 0) {
			elementStatus.textContent = "Свободных мест нет";
		} else {
			elementStatus.textContent = "Доступно следующее время:";

			listTime.forEach((timestamp, index) => {
				const timeRadio = document.createElement("input");
				timeRadio.type = "radio";
				timeRadio.className = "btn-check";
				timeRadio.id = `timeChoice${index}`;
				timeRadio.name = "radio";
				timeRadio.value = moment(timestamp).toISOString();
				timeRadio.addEventListener("click", () => (btnSubmit.disabled = false));
				timeRadio.autocomplete = "off";

				const labelTime = document.createElement("label");
				labelTime.className = "btn btn-outline-success";
				labelTime.setAttribute("for", `timeChoice${index}`);
				labelTime.textContent = moment(timestamp).format("LT");

				elementTime.append(timeRadio, labelTime);
			});
		}
	}
});
