"use strict";

document.addEventListener("DOMContentLoaded", function () {
	function addingPhoneNumber() {
		const matrix = "+38(___) ___-__-__";
		const def = matrix.replace(/\D/g, "");
		let val = this.value.replace(/\D/g, "");
		let i = 0;
		if (def.length >= val.length) {
			val = def;
		}
		this.value = matrix.replace(/./g, (match) => {
			if (/[_\d]/.test(match) && i < val.length) {
				return val[i++];
			}
			if (i < val.length) {
				return match;
			}
			return "";
		});
	}

	const phoneInput = document.querySelector("#phone");
	for (let env of ["input", "focus", "blur"]) {
		phoneInput.addEventListener(env, addingPhoneNumber);
	}
});
