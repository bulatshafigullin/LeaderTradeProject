'use strict';

const gulp = require('gulp');
const sass = require('gulp-sass')(require('sass'));
var csso = require('gulp-csso');

function buildStyles() {
  return gulp.src('./css/**/*.scss')
    .pipe(sass.sync().on('error', sass.logError))
    .pipe(gulp.dest('./css'));
};

gulp.task('compress', function () {
    return gulp.src('./css/style.css')
        .pipe(csso())
        .pipe(gulp.dest('./css'));
});

exports.buildStyles = buildStyles;
exports.watch = function () {
  gulp.watch('./css/**/*.scss', buildStyles);
};