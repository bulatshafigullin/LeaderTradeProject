$('.catalog-btn').click(function () {
	$(this).toggleClass('active');
	$('.catalog-menu').slideToggle(500)
})

//menu mobile
$('.mobile-menu--trigger').click(function (e) {
	e.preventDefault();
	$(this).toggleClass('active');
	$('.mobile-fade').fadeToggle(0);
	$('body').toggleClass('hidden-body');
})

Fancybox.bind("[data-fancybox]", {
});
Fancybox.bind("[data-fancybox='gallery']", {
});

IMask(
	document.getElementById('phone-mask'),
	{
		mask: '+{7}(000)000-00-00'
	}
)
const swiper = new Swiper('.mainHeader__left', {
	slidesPerView: 1,
	spaceBetween: 10,
	pagination: {
		el: '.mainHeader__page',
	},
});

document.querySelectorAll('.items-slider').forEach(n => { //можно указать контейнер, в который помещён каждый слайдер
	let slider3 = new Swiper(n.querySelector('.items-slider-wrapper'), {
		navigation: {
			prevEl: n.querySelector('.items-slider .slider-left'),
			nextEl: n.querySelector('.items-slider .slider-right'),
		},
		slidesPerView: 6,
		spaceBetween: 10,
		breakpoints: {
			200: {
				slidesPerView: 2,
			},
			600: {
				slidesPerView: 3,
			},
			980: {
				slidesPerView: 4,
			},
			1100: {
				slidesPerView: 5,
			},
			1321: {
				slidesPerView: 6,
			},
		}
	});
});

document.querySelectorAll('.portfolio-container').forEach(n => { //можно указать контейнер, в который помещён каждый слайдер
	let slider4 = new Swiper(n.querySelector('.portfolio-slider'), {
		navigation: {
			prevEl: n.querySelector('.portfolio-container .slider-left'),
			nextEl: n.querySelector('.portfolio-container .slider-right'),
		},
		slidesPerView: 3,
		spaceBetween: 20,
		breakpoints: {
			200: {
				slidesPerView: 2,
			},
			600: {
				slidesPerView: 3,
			},

		}
	});
});

const sliderNews = new Swiper('.news-slider', {
	slidesPerView: 3,
	spaceBetween: 15,
	breakpoints: {
		200: {
			slidesPerView: 2,
		},
		600: {
			slidesPerView: 3,
		},
		980: {
			slidesPerView: 3,
		}
	},
	navigation: {
		prevEl: '.news-slider .slider-left',
		nextEl: '.news-slider .slider-right',
	},
});

const swiper3 = new Swiper('.promo-slider', {
	slidesPerView: 3,
	spaceBetween: 15,
	breakpoints: {
		200: {
			slidesPerView: 1,
		},
		600: {
			slidesPerView: 2,
		},
		980: {
			slidesPerView: 3,
		}
	},
	navigation: {
		prevEl: '.promo .slider-left',
		nextEl: '.promo .slider-right',
	},
});

if (window.innerWidth < 1024) {
	const swiper4 = new Swiper('.menu-slider', {
		slidesPerView: 'auto',
		spaceBetween: 15,
	});
}

const swiper5 = new Swiper('.about-reviews-slider', {
	slidesPerView: 3,
	spaceBetween: 15,
	breakpoints: {
		200: {
			slidesPerView: 1,
		},
		600: {
			slidesPerView: 2,
		},
		1200: {
			slidesPerView: 3,
		}
	},
	navigation: {
		prevEl: '.about-reviews .slider-left',
		nextEl: '.about-reviews .slider-right',
	},
});

$(function () {
	$(".selectize").selectize();
});
$(function () {
	$(".select").selectize({
		allowEmptyOption: true,
		onChange: function(e, v) {
			var form = this.$input["0"].closest('form')

			if (form && form.hasAttribute('ts-req')) {
				var event = new Event("submit")
				form.dispatchEvent(event)
			}
		}
	});
});

$('.faq__item').click(function () {
	$(this).toggleClass('faq__item--active')
})

$('.catalog__right__selector').on('click', function (e) {
	e.preventDefault();
	$(this)
		.addClass('lk-selector--active').siblings().removeClass('lk-selector--active')
	$('.lk__right__wrapper').find('.lk__right__item').removeClass('item--active').eq($(this).index()).addClass('item--active');
});

$('.contactsMain__city').on('click', function (e) {
	e.preventDefault();
	$(this)
		.addClass('active').siblings().removeClass('active')
	$('.contactsMain__wrapper').find('.contactsMain__mapItem').removeClass('active').eq($(this).index()).addClass('active');
});


$('.checkbox input').on('change', function () {
	let check = $(this);
	if (check.is(':checked')) {
		check.parents('.checkbox').addClass('checkbox--active')

	} else {
		check.parents('.checkbox').removeClass('checkbox--active')

	}
})
$('.radio input').on('change', function () {
	let check = $(this);
	if (check.is(':checked')) {
		check.parents('.radio').siblings('.radio').removeClass('checkbox--active')
		check.parents('.radio').addClass('checkbox--active')
	} else {
		check.parents('.radio').removeClass('checkbox--active')

	}
})


$('.catalog__moar').click(function () {
	$(this).siblings('.catalog__checkboxes').addClass('catalog__checkboxes--active');
	$(this).hide()
})

$('.like').click(function () {
	$(this).toggleClass('like--active')
})

let currentValue = 1;
$(document).ready(function () {
	$('.cart__left__calc__plus').click(function () {
		$(this).siblings('.cart__left__calc__num').val(currentValue++)
	});
	$('.cart__left__calc__minus').click(function () {
		if (currentValue > 0) {
			$(this).siblings('.cart__left__calc__num').val(currentValue--)
		}
	});
});

$('.cart__right__item input').on('change', function () {
	if ($(this).is(":checked")) {
		$('.cart__right__item').removeClass('cart__right__item--active');
		$(this).parents('.cart__right__item').addClass('cart__right__item--active');
	} else {
		$(this).parents('.cart__right__item').removeClass('cart__right__item--active')
	}
})

var lightGalleryEl = document.getElementById('lightgallery')
if (lightGalleryEl) {
	lightGallery(lightGalleryEl, {
		speed: 500,
	});
}


//range slider

let fromRange = $('#fromRange')
let toRange = $('#toRange')
var slider = document.getElementById('slider');
let dataFrom = parseFloat(fromRange.data('from'))
let dataTo = parseFloat(toRange.data('to'))

if (slider) {
	noUiSlider.create(slider, {
		start: [dataFrom, dataTo],
		connect: true,
		decimals: 0,
		step: 1,
		range: {
			'min': dataFrom,
			'max': dataTo
		},
		format:{
            to: (v) => parseFloat(v).toFixed(0),
            from: (v) => parseFloat(v).toFixed(0)
        },

	});

	slider.noUiSlider.on('update', function (values) {
		fromRange.val(values[0])
		toRange.val(values[1])
	});

	slider.noUiSlider.on("change", (a, b)=> {
        var event = new Event('submit');
		fromRange.closest('form')[0].dispatchEvent(event)
	})

}


twinspark.func({
	"openFancy": (o) => {
		Fancybox.show([{ src: o.el.getAttribute("ts-target"), type: "inline" }]);
	},
	"fire": (eventName, sel, o) => {
		var event = new Event(eventName);
		document.querySelector(sel).dispatchEvent(event)
	}
})

function setPageMeta(name, val) {
	var m = document.querySelector('meta[name="'+name+'"]');
	m && m.setAttribute("content", val);
}