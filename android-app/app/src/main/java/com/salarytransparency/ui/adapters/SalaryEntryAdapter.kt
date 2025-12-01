package com.salarytransparency.ui.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.salarytransparency.R
import com.salarytransparency.data.model.SalaryEntry
import java.text.NumberFormat
import java.util.*

class SalaryEntryAdapter : ListAdapter<SalaryEntry, SalaryEntryAdapter.ViewHolder>(DiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_salary_entry, parent, false)
        return ViewHolder(view)
    }
    
    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
    
    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tvJobTitle: TextView = itemView.findViewById(R.id.tv_job_title)
        private val tvCompany: TextView = itemView.findViewById(R.id.tv_company)
        private val tvSalary: TextView = itemView.findViewById(R.id.tv_salary)
        private val tvExperience: TextView = itemView.findViewById(R.id.tv_experience)
        private val tvLocation: TextView = itemView.findViewById(R.id.tv_location)
        private val tvEducation: TextView = itemView.findViewById(R.id.tv_education)
        
        fun bind(entry: SalaryEntry) {
            val formatter = NumberFormat.getCurrencyInstance(Locale.US)
            
            tvJobTitle.text = entry.jobTitle
            tvCompany.text = "${entry.company} - ${entry.industry}"
            tvSalary.text = formatter.format(entry.salaryUsd)
            tvExperience.text = "${entry.yearsOfExperience} yrs"
            tvLocation.text = "${entry.location}, ${entry.country}"
            tvEducation.text = entry.educationLevel
        }
    }
    
    private class DiffCallback : DiffUtil.ItemCallback<SalaryEntry>() {
        override fun areItemsTheSame(oldItem: SalaryEntry, newItem: SalaryEntry): Boolean {
            return oldItem.id == newItem.id
        }
        
        override fun areContentsTheSame(oldItem: SalaryEntry, newItem: SalaryEntry): Boolean {
            return oldItem == newItem
        }
    }
}
