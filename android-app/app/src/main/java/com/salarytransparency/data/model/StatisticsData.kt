package com.salarytransparency.data.model

data class StatisticsData(
    val totalEntries: Int,
    val averageSalary: Double,
    val medianSalary: Double,
    val minSalary: Double,
    val maxSalary: Double,
    val industryDistribution: Map<String, Int>,
    val experienceDistribution: Map<String, Int>,
    val educationDistribution: Map<String, Int>,
    val genderDistribution: Map<String, Int>
)
