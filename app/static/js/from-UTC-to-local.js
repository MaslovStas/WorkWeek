"use strict";

document.addEventListener("DOMContentLoaded", () => {
	const begin_of_the_day = document.querySelector("#begin_of_the_day");
	const end_of_the_day = document.querySelector("#end_of_the_day");
	for (let input of [begin_of_the_day, end_of_the_day]) {
		let list_time = input.value.split(":");
		input.value = moment()
			.utc()
			.set({ hour: list_time[0], minute: list_time[1] })
			.local()
			.format("HH:mm");
	}
});
