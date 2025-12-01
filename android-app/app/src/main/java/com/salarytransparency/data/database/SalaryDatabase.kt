package com.salarytransparency.data.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.salarytransparency.data.dao.SalaryDao
import com.salarytransparency.data.model.SalaryEntry

@Database(entities = [SalaryEntry::class], version = 1, exportSchema = false)
abstract class SalaryDatabase : RoomDatabase() {
    abstract fun salaryDao(): SalaryDao
    
    companion object {
        @Volatile
        private var INSTANCE: SalaryDatabase? = null
        
        fun getDatabase(context: Context): SalaryDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    SalaryDatabase::class.java,
                    "salary_database"
                )
                    .fallbackToDestructiveMigration()
                    .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
