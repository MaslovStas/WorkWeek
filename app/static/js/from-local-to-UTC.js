"use strict";

document.addEventListener("DOMContentLoaded", () => {
	let form = document.querySelector("form");
	form.addEventListener("submit", formSend);

	async function formSend(event) {
		try {
			event.preventDefault();

			let formData = new FormData(form);
			formData.set(
				"begin_of_the_day",
				fromLocalToUTC(formData.get("begin_of_the_day"))
			);
			formData.set(
				"end_of_the_day",
				fromLocalToUTC(formData.get("end_of_the_day"))
			);

			let response = await fetch(form.action, {
				method: "POST",
				body: formData,
			});

			if (!response.ok) throw new Error();
			if (response.redirected) document.location.href = response.url;
		} catch (error) {
			alert("Ошибка соединения с сервером. Попробуйте еще раз");
		}
	}

	function fromLocalToUTC(time) {
		let list_time = time.split(":");
		return moment()
			.set({ hour: list_time[0], minute: list_time[1] })
			.utc()
			.format("HH:mm");
	}
});
