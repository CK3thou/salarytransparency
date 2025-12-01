package com.salarytransparency.utils

import com.opencsv.CSVReader
import com.opencsv.CSVWriter
import com.salarytransparency.data.model.SalaryEntry
import java.io.InputStream
import java.io.OutputStream
import java.io.InputStreamReader
import java.io.OutputStreamWriter

object CsvHelper {
    
    fun exportToCsv(entries: List<SalaryEntry>, outputStream: OutputStream) {
        val writer = CSVWriter(OutputStreamWriter(outputStream))
        
        // Write header
        val header = arrayOf(
            "Job Title", "Company", "Industry", "Currency", "Salary", "Salary USD",
            "Years of Experience", "Education Level", "Location", "Country",
            "Nationality", "Gender", "Age", "Benefits"
        )
        writer.writeNext(header)
        
        // Write data
        entries.forEach { entry ->
            val row = arrayOf(
                entry.jobTitle,
                entry.company,
                entry.industry,
                entry.currency,
                entry.salary.toString(),
                entry.salaryUsd.toString(),
                entry.yearsOfExperience.toString(),
                entry.educationLevel,
                entry.location,
                entry.country,
                entry.nationality,
                entry.gender,
                entry.age.toString(),
                entry.benefits
            )
            writer.writeNext(row)
        }
        
        writer.close()
    }
    
    fun importFromCsv(inputStream: InputStream): List<SalaryEntry> {
        val reader = CSVReader(InputStreamReader(inputStream))
        val entries = mutableListOf<SalaryEntry>()
        
        // Skip header
        reader.readNext()
        
        var line: Array<String>? = reader.readNext()
        while (line != null) {
            try {
                val entry = SalaryEntry(
                    jobTitle = line.getOrNull(0) ?: "",
                    company = line.getOrNull(1) ?: "",
                    industry = line.getOrNull(2) ?: "Other",
                    currency = line.getOrNull(3) ?: "USD",
                    salary = line.getOrNull(4)?.toDoubleOrNull() ?: 0.0,
                    salaryUsd = line.getOrNull(5)?.toDoubleOrNull() ?: 0.0,
                    yearsOfExperience = line.getOrNull(6)?.toIntOrNull() ?: 0,
                    educationLevel = line.getOrNull(7) ?: "Not specified",
                    location = line.getOrNull(8) ?: "Not specified",
                    country = line.getOrNull(9) ?: "Not specified",
                    nationality = line.getOrNull(10) ?: "Not specified",
                    gender = line.getOrNull(11) ?: "Prefer not to say",
                    age = line.getOrNull(12)?.toIntOrNull() ?: 0,
                    benefits = line.getOrNull(13) ?: ""
                )
                entries.add(entry)
            } catch (e: Exception) {
                // Skip invalid rows
            }
            line = reader.readNext()
        }
        
        reader.close()
        return entries
    }
}
