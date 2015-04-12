'use strict';

var gulp = require('gulp');
var browserify = require('gulp-browserify');
var size = require('gulp-size');
var clean = require('gulp-clean');
var sass = require('gulp-sass');


gulp.task('transform', function() {
    return gulp.src('./project/static/scripts/jsx/main.js')
        .pipe(browserify({transform: ['reactify']}))
        .pipe(gulp.dest('./project/static/scripts/js'))
        .pipe(size());
});

gulp.task('sass', function() {
    return gulp.src('./project/static/styles/scss/*.scss')
        .pipe(sass())
        .pipe(gulp.dest('./project/static/styles/css'));
});

gulp.task('clean', function() {
    return gulp.src(['./project/static/scripts/js', './project/static/styles/css'], {read: false})
        .pipe(clean());
});


gulp.task('default', ['clean', 'sass'], function() {
    gulp.start('transform');
    gulp.watch('./project/static/scripts/jsx/main.js', ['transform']);
});
