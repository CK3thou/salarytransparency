package com.salarytransparency.ui.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.AutoCompleteTextView
import android.widget.Button
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.google.android.material.textfield.TextInputEditText
import com.salarytransparency.R
import com.salarytransparency.data.model.SalaryEntry
import com.salarytransparency.viewmodel.SalaryViewModel

class SubmitFragment : Fragment() {
    
    private val viewModel: SalaryViewModel by activityViewModels()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_submit, container, false)
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupDropdowns(view)
        setupSubmitButton(view)
    }
    
    private fun setupDropdowns(view: View) {
        val educationAdapter = ArrayAdapter(
            requireContext(),
            android.R.layout.simple_dropdown_item_1line,
            resources.getStringArray(R.array.education_levels)
        )
        view.findViewById<AutoCompleteTextView>(R.id.et_education).setAdapter(educationAdapter)
        
        val genderAdapter = ArrayAdapter(
            requireContext(),
            android.R.layout.simple_dropdown_item_1line,
            resources.getStringArray(R.array.gender_options)
        )
        view.findViewById<AutoCompleteTextView>(R.id.et_gender).setAdapter(genderAdapter)
        
        val currencyAdapter = ArrayAdapter(
            requireContext(),
            android.R.layout.simple_dropdown_item_1line,
            resources.getStringArray(R.array.currency_options)
        )
        view.findViewById<AutoCompleteTextView>(R.id.et_currency).setAdapter(currencyAdapter)
        
        // Set default currency
        view.findViewById<AutoCompleteTextView>(R.id.et_currency).setText("USD", false)
    }
    
    private fun setupSubmitButton(view: View) {
        view.findViewById<Button>(R.id.btn_submit).setOnClickListener {
            if (validateAndSubmit(view)) {
                Toast.makeText(requireContext(), R.string.submit_success, Toast.LENGTH_SHORT).show()
                clearForm(view)
            } else {
                Toast.makeText(requireContext(), R.string.submit_error, Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun validateAndSubmit(view: View): Boolean {
        try {
            val jobTitle = view.findViewById<TextInputEditText>(R.id.et_job_title).text.toString()
            val company = view.findViewById<TextInputEditText>(R.id.et_company).text.toString()
            val industry = view.findViewById<AutoCompleteTextView>(R.id.et_industry).text.toString()
            val salaryStr = view.findViewById<TextInputEditText>(R.id.et_salary).text.toString()
            val currency = view.findViewById<AutoCompleteTextView>(R.id.et_currency).text.toString()
            val experienceStr = view.findViewById<TextInputEditText>(R.id.et_years_experience).text.toString()
            val education = view.findViewById<AutoCompleteTextView>(R.id.et_education).text.toString()
            val location = view.findViewById<TextInputEditText>(R.id.et_location).text.toString()
            val country = view.findViewById<TextInputEditText>(R.id.et_country).text.toString()
            val nationality = view.findViewById<TextInputEditText>(R.id.et_nationality).text.toString()
            val gender = view.findViewById<AutoCompleteTextView>(R.id.et_gender).text.toString()
            val ageStr = view.findViewById<TextInputEditText>(R.id.et_age).text.toString()
            val benefits = view.findViewById<TextInputEditText>(R.id.et_benefits).text.toString()
            
            if (jobTitle.isBlank() || company.isBlank() || salaryStr.isBlank() || experienceStr.isBlank()) {
                return false
            }
            
            val salary = salaryStr.toDoubleOrNull() ?: return false
            val experience = experienceStr.toIntOrNull() ?: return false
            val age = ageStr.toIntOrNull() ?: 0
            
            // Simple currency conversion (in real app, use actual exchange rates)
            val salaryUsd = when (currency) {
                "ZMW" -> salary / 27.0
                "EUR" -> salary * 1.08
                "GBP" -> salary * 1.27
                else -> salary
            }
            
            val entry = SalaryEntry(
                jobTitle = jobTitle,
                company = company,
                industry = industry.ifBlank { "Other" },
                currency = currency,
                salary = salary,
                salaryUsd = salaryUsd,
                yearsOfExperience = experience,
                educationLevel = education.ifBlank { "Not specified" },
                location = location.ifBlank { "Not specified" },
                country = country.ifBlank { "Not specified" },
                nationality = nationality.ifBlank { "Not specified" },
                gender = gender.ifBlank { "Prefer not to say" },
                age = age,
                benefits = benefits
            )
            
            viewModel.insert(entry)
            return true
        } catch (e: Exception) {
            return false
        }
    }
    
    private fun clearForm(view: View) {
        view.findViewById<TextInputEditText>(R.id.et_job_title).text?.clear()
        view.findViewById<TextInputEditText>(R.id.et_company).text?.clear()
        view.findViewById<AutoCompleteTextView>(R.id.et_industry).text?.clear()
        view.findViewById<TextInputEditText>(R.id.et_salary).text?.clear()
        view.findViewById<TextInputEditText>(R.id.et_years_experience).text?.clear()
        view.findViewById<AutoCompleteTextView>(R.id.et_education).text?.clear()
        view.findViewById<TextInputEditText>(R.id.et_location).text?.clear()
        view.findViewById<TextInputEditText>(R.id.et_country).text?.clear()
        view.findViewById<TextInputEditText>(R.id.et_nationality).text?.clear()
        view.findViewById<AutoCompleteTextView>(R.id.et_gender).text?.clear()
        view.findViewById<TextInputEditText>(R.id.et_age).text?.clear()
        view.findViewById<TextInputEditText>(R.id.et_benefits).text?.clear()
    }
}
