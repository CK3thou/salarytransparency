package com.salarytransparency.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "salary_entries")
data class SalaryEntry(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val jobTitle: String,
    val company: String,
    val industry: String,
    val currency: String,
    val salary: Double,
    val salaryUsd: Double,
    val yearsOfExperience: Int,
    val educationLevel: String,
    val location: String,
    val country: String,
    val nationality: String,
    val gender: String,
    val age: Int,
    val benefits: String,
    val submissionDate: Long = System.currentTimeMillis()
)
