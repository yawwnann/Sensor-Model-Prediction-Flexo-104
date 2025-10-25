"""
Downtime Service
Service untuk analisis dan agregasi data downtime dari machine_logs
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from src.services.database_service import db_service
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DowntimeService:
    """Service untuk analisis downtime berdasarkan machine_logs."""
    
    # Mapping status ke kategori downtime
    DOWNTIME_STATUS = {
        'Error': 'error',
        'Stopped': 'stopped',
        'Idle': 'idle',
        'Maintenance': 'maintenance'
    }
    
    def get_downtime_history(
        self, 
        limit: int = 50,
        component_filter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Menganalisis machine_logs untuk menghasilkan history downtime.
        
        Args:
            limit: Maksimal jumlah downtime events yang dikembalikan
            component_filter: Filter berdasarkan komponen (opsional)
            start_date: Filter tanggal mulai (format: YYYY-MM-DD)
            end_date: Filter tanggal akhir (format: YYYY-MM-DD)
            
        Returns:
            List of downtime events dengan detail lengkap
        """
        try:
            logger.info("=" * 60)
            logger.info("DOWNTIME DETECTION - STARTING")
            logger.info(f"Parameters: limit={limit}, component={component_filter}, start={start_date}, end={end_date}")
            logger.info("=" * 60)
            
            # PRIORITY: Analyze health drops from machine_logs (REAL DATA)
            logger.info("🔍 [STEP 1] Analyzing downtime from machine_logs performance/quality metrics")
            downtime_from_health = self._analyze_health_drops(limit, start_date, end_date)
            
            if downtime_from_health:
                # Filter berdasarkan komponen jika diminta
                if component_filter and component_filter.lower() != 'all':
                    downtime_from_health = [
                        event for event in downtime_from_health 
                        if event['component'].lower() == component_filter.lower()
                    ]
                
                logger.info(f"Generated {len(downtime_from_health)} downtime events from health analysis")
                return downtime_from_health
            
            # FALLBACK: Try status-based detection
            logs = self._fetch_machine_logs(limit * 10, start_date, end_date)
            
            if not logs:
                logger.warning("No machine logs available for downtime analysis")
                return []
            
            # Analisis logs untuk menemukan downtime periods
            downtime_events = self._analyze_downtime_periods(logs)
            
            # Filter berdasarkan komponen jika diminta
            if component_filter and component_filter.lower() != 'all':
                downtime_events = [
                    event for event in downtime_events 
                    if event['component'].lower() == component_filter.lower()
                ]
            
            # Limit hasil
            downtime_events = downtime_events[:limit]
            
            logger.info(f"Generated {len(downtime_events)} downtime events from status analysis")
            return downtime_events
            
        except Exception as e:
            logger.error(f"Error generating downtime history: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_downtime_statistics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Menghitung statistik downtime.
        
        Args:
            start_date: Filter tanggal mulai (format: YYYY-MM-DD)
            end_date: Filter tanggal akhir (format: YYYY-MM-DD)
            
        Returns:
            Dict dengan statistik downtime
        """
        try:
            downtime_events = self.get_downtime_history(
                limit=1000, 
                start_date=start_date, 
                end_date=end_date
            )
            
            if not downtime_events:
                return {
                    "total_downtime": 0,
                    "total_duration_minutes": 0,
                    "average_duration_minutes": 0,
                    "preventive_count": 0,
                    "reactive_count": 0,
                    "by_component": {},
                    "by_severity": {
                        "low": 0,
                        "medium": 0,
                        "high": 0,
                        "critical": 0
                    }
                }
            
            # Hitung statistik
            total_duration = sum(event['duration'] for event in downtime_events)
            preventive = sum(1 for e in downtime_events if e['type'] == 'preventive')
            reactive = sum(1 for e in downtime_events if e['type'] == 'reactive')
            
            # Agregasi per komponen
            by_component = {}
            for event in downtime_events:
                comp = event['component']
                if comp not in by_component:
                    by_component[comp] = {
                        "count": 0,
                        "total_duration": 0
                    }
                by_component[comp]["count"] += 1
                by_component[comp]["total_duration"] += event['duration']
            
            # Agregasi per severity
            by_severity = {
                "low": sum(1 for e in downtime_events if e['severity'] == 'low'),
                "medium": sum(1 for e in downtime_events if e['severity'] == 'medium'),
                "high": sum(1 for e in downtime_events if e['severity'] == 'high'),
                "critical": sum(1 for e in downtime_events if e['severity'] == 'critical')
            }
            
            return {
                "total_downtime": len(downtime_events),
                "total_duration_minutes": total_duration,
                "average_duration_minutes": round(total_duration / len(downtime_events), 2),
                "preventive_count": preventive,
                "reactive_count": reactive,
                "by_component": by_component,
                "by_severity": by_severity
            }
            
        except Exception as e:
            logger.error(f"Error calculating downtime statistics: {e}")
            return {
                "total_downtime": 0,
                "total_duration_minutes": 0,
                "average_duration_minutes": 0,
                "preventive_count": 0,
                "reactive_count": 0,
                "by_component": {},
                "by_severity": {}
            }
    
    def _fetch_machine_logs(
        self, 
        limit: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch machine logs dari database dengan filter opsional.
        
        Args:
            limit: Maksimal jumlah logs
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            
        Returns:
            List of machine logs
        """
        try:
            with db_service.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Build query dengan filter date
                    query = """
                        SELECT 
                            timestamp, 
                            machine_status, 
                            performance_rate,
                            quality_rate
                        FROM machine_logs
                        WHERE 1=1
                    """
                    params = []
                    
                    if start_date:
                        query += " AND timestamp >= %s"
                        params.append(start_date)
                    
                    if end_date:
                        query += " AND timestamp <= %s"
                        params.append(end_date)
                    
                    query += " ORDER BY timestamp DESC LIMIT %s"
                    params.append(limit)
                    
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    
                    logs = []
                    for row in results:
                        logs.append({
                            "timestamp": row[0],
                            "machine_status": row[1],
                            "performance_rate": row[2],
                            "quality_rate": row[3]
                        })
                    
                    return logs
                    
        except Exception as e:
            logger.error(f"Error fetching machine logs: {e}")
            return []
    
    def _analyze_downtime_periods(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Menganalisis logs untuk menemukan periode downtime.
        
        Args:
            logs: List of machine logs (sorted DESC by timestamp)
            
        Returns:
            List of downtime events
        """
        downtime_events = []
        current_downtime = None
        
        # Reverse agar urutan ascending (dari lama ke baru)
        logs = list(reversed(logs))
        
        for i, log in enumerate(logs):
            status = log['machine_status']
            
            # Deteksi mulai downtime
            if status in self.DOWNTIME_STATUS and current_downtime is None:
                current_downtime = {
                    'start_time': log['timestamp'],
                    'status': status,
                    'performance_rate': log.get('performance_rate', 0),
                    'quality_rate': log.get('quality_rate', 0)
                }
            
            # Deteksi akhir downtime (kembali Running)
            elif status == 'Running' and current_downtime is not None:
                end_time = log['timestamp']
                duration = self._calculate_duration(
                    current_downtime['start_time'], 
                    end_time
                )
                
                # Buat downtime event
                event = self._create_downtime_event(
                    current_downtime,
                    end_time,
                    duration
                )
                downtime_events.append(event)
                
                current_downtime = None
        
        # Handle downtime yang masih berlangsung
        if current_downtime is not None:
            end_time = datetime.now()
            duration = self._calculate_duration(
                current_downtime['start_time'],
                end_time
            )
            event = self._create_downtime_event(
                current_downtime,
                end_time,
                duration
            )
            event['ongoing'] = True
            downtime_events.append(event)
        
        # Reverse untuk menampilkan yang terbaru dulu
        return list(reversed(downtime_events))
    
    def _calculate_duration(self, start_time, end_time) -> int:
        """
        Menghitung durasi dalam menit.
        
        Args:
            start_time: Waktu mulai (datetime atau string)
            end_time: Waktu selesai (datetime atau string)
            
        Returns:
            Durasi dalam menit (integer)
        """
        try:
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            delta = end_time - start_time
            return int(delta.total_seconds() / 60)
        except Exception as e:
            logger.error(f"Error calculating duration: {e}")
            return 0
    
    def _create_downtime_event(
        self, 
        downtime_info: Dict[str, Any],
        end_time,
        duration: int
    ) -> Dict[str, Any]:
        """
        Membuat event downtime dari informasi yang terkumpul.
        
        Args:
            downtime_info: Informasi downtime (start_time, status, etc)
            end_time: Waktu selesai downtime
            duration: Durasi dalam menit
            
        Returns:
            Dict dengan detail downtime event
        """
        status = downtime_info['status']
        
        # Tentukan severity berdasarkan durasi dan status
        severity = self._determine_severity(duration, status)
        
        # Tentukan komponen yang terdampak (analisis sederhana)
        component = self._identify_affected_component(
            downtime_info.get('performance_rate', 0),
            downtime_info.get('quality_rate', 0)
        )
        
        # Tentukan tipe (preventive vs reactive)
        event_type = 'preventive' if status == 'Maintenance' else 'reactive'
        
        # Generate alasan downtime
        reason = self._generate_downtime_reason(status, component)
        
        # Format timestamp
        start_str = downtime_info['start_time']
        if isinstance(start_str, datetime):
            start_str = start_str.isoformat()
        
        end_str = end_time
        if isinstance(end_str, datetime):
            end_str = end_str.isoformat()
        
        return {
            "id": f"DT-{int(datetime.now().timestamp() * 1000) % 100000}",
            "timestamp": start_str,
            "end_timestamp": end_str,
            "component": component,
            "reason": reason,
            "duration": duration,
            "type": event_type,
            "severity": severity,
            "status": "resolved",
            "technician": "Auto-detected",
            "notes": f"Detected from machine_logs. Status: {status}"
        }
    
    def _determine_severity(self, duration: int, status: str) -> str:
        """
        Menentukan severity berdasarkan durasi dan status.
        
        Args:
            duration: Durasi dalam menit
            status: Status mesin
            
        Returns:
            Severity level (low/medium/high/critical)
        """
        if status == 'Error':
            if duration > 120:
                return 'critical'
            elif duration > 60:
                return 'high'
            else:
                return 'medium'
        elif status == 'Maintenance':
            return 'low' if duration < 60 else 'medium'
        else:
            if duration > 180:
                return 'critical'
            elif duration > 90:
                return 'high'
            elif duration > 30:
                return 'medium'
            else:
                return 'low'
    
    def _identify_affected_component(self, performance: float, quality: float) -> str:
        """
        Identifikasi komponen yang kemungkinan bermasalah.
        
        Args:
            performance: Performance rate
            quality: Quality rate
            
        Returns:
            Nama komponen
        """
        # Logika sederhana untuk menentukan komponen
        if quality < 80:
            return 'Printing'
        elif performance < 70:
            return 'Feeder'
        elif performance < 85:
            return 'Pre-Feeder'
        else:
            # Rotasi komponen untuk variasi
            import random
            components = ['Pre-Feeder', 'Feeder', 'Printing', 'Slotter', 'Stacker']
            return random.choice(components)
    
    def _generate_downtime_reason(self, status: str, component: str) -> str:
        """
        Generate alasan downtime berdasarkan status dan komponen.
        
        Args:
            status: Status mesin
            component: Komponen terdampak
            
        Returns:
            String alasan downtime
        """
        reasons = {
            'Error': f'{component} malfunction detected',
            'Maintenance': f'Scheduled maintenance on {component}',
            'Stopped': f'{component} stopped - investigation required',
            'Idle': f'{component} idle - awaiting material'
        }
        return reasons.get(status, f'{component} downtime detected')
    
    # MOCK DATA GENERATOR DISABLED - ONLY USE REAL DATA FROM machine_logs
    # def _generate_mock_downtime_events(self, limit: int = 50) -> List[Dict[str, Any]]:
    #     """Mock data generator - DISABLED for production"""
    #     logger.warning("Mock data generator is disabled. Only real data from machine_logs is used.")
    #     return []
    
    def _analyze_health_drops(
        self,
        limit: int = 50,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Menganalisis health drops dari machine_logs berdasarkan OEE/Performance/Quality drops.
        Deteksi ketika metrics turun drastis (indikasi downtime).
        
        Args:
            limit: Maksimal events
            start_date: Filter start date
            end_date: Filter end date
            
        Returns:
            List of downtime events detected from metric drops
        """
        try:
            # Fetch machine logs dengan semua metrics
            with db_service.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            timestamp,
                            machine_status,
                            performance_rate,
                            quality_rate,
                            cumulative_production,
                            cumulative_defects
                        FROM machine_logs
                        WHERE 1=1
                    """
                    params = []
                    
                    if start_date:
                        query += " AND timestamp >= %s"
                        params.append(start_date)
                    
                    if end_date:
                        query += " AND timestamp <= %s"
                        params.append(end_date)
                    
                    query += " ORDER BY timestamp ASC LIMIT %s"
                    params.append(limit * 10)
                    
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    
                    logger.info(f"📊 Query returned {len(results) if results else 0} machine_logs records")
                    
                    if not results:
                        logger.warning("❌ No machine logs found for health analysis")
                        logger.warning("💡 TIP: Run sensor_simulator.py to populate machine_logs table")
                        return []
                    
                    # Log sample data untuk debugging
                    if results:
                        sample = results[0]
                        logger.info(f"📝 Sample data: timestamp={sample[0]}, status={sample[1]}, perf={sample[2]}, qual={sample[3]}")
                    
                    # Analyze untuk menemukan drops (performance < 20% atau quality < 20%)
                    events = []
                    critical_count = 0
                    in_downtime = False
                    downtime_start = None
                    downtime_start_metrics = None
                    
                    logger.info(f"🔍 Analyzing {len(results)} machine log records for downtime patterns...")
                    
                    for i, row in enumerate(results):
                        timestamp = row[0]
                        status = row[1]
                        performance = float(row[2] or 0)
                        quality = float(row[3] or 0)
                        
                        # Deteksi downtime: performance atau quality < 20% ATAU status bukan 'Running'
                        is_critical = (
                            performance < 20 or 
                            quality < 20 or 
                            status != 'Running' or
                            status == 'Downtime' or
                            status in self.DOWNTIME_STATUS
                        )
                        
                        if is_critical:
                            critical_count += 1
                            if critical_count <= 5:  # Log first 5 critical events
                                logger.info(f"🔴 Critical #{critical_count}: P={performance:.1f}% Q={quality:.1f}% Status={status} at {timestamp}")
                        
                        if is_critical and not in_downtime:
                            # Start downtime
                            in_downtime = True
                            downtime_start = timestamp
                            downtime_start_metrics = {
                                'performance': performance,
                                'quality': quality,
                                'status': status
                            }
                            logger.info(f"🟡 Downtime started at {timestamp}")
                        
                        elif not is_critical and in_downtime:
                            # End downtime
                            in_downtime = False
                            downtime_end = timestamp
                            
                            # Calculate duration
                            duration = self._calculate_duration(downtime_start, downtime_end)
                            logger.info(f"🟢 Downtime ended at {timestamp}, duration: {duration} minutes")
                            
                            if duration >= 0:  # Record all events for now (including 0-minute events)
                                # Determine component based on which metric dropped
                                if downtime_start_metrics['quality'] < 20:
                                    component = 'Printing'
                                elif downtime_start_metrics['performance'] < 30:
                                    component = 'Feeder'
                                elif downtime_start_metrics['performance'] < 50:
                                    component = 'Pre-Feeder'
                                else:
                                    components = ['Slotter', 'Stacker']
                                    import random
                                    component = random.choice(components)
                                
                                # Determine severity
                                severity = self._determine_severity(duration, downtime_start_metrics['status'])
                                
                                # Format duration for display (convert 0-minute events to show seconds)
                                if duration == 0:
                                    # Calculate seconds for very short downtime
                                    if hasattr(downtime_start, 'timestamp') and hasattr(downtime_end, 'timestamp'):
                                        duration_seconds = int((downtime_end.timestamp() - downtime_start.timestamp()))
                                        duration_display = max(duration_seconds, 1)  # Minimum 1 minute for display
                                    else:
                                        duration_display = 1
                                else:
                                    duration_display = duration
                                
                                event = {
                                    "id": f"DT-{int(downtime_start.timestamp() * 1000) % 100000}" if hasattr(downtime_start, 'timestamp') else f"DT-{len(events)}",
                                    "timestamp": downtime_start.isoformat() if hasattr(downtime_start, 'isoformat') else str(downtime_start),
                                    "end_timestamp": downtime_end.isoformat() if hasattr(downtime_end, 'isoformat') else str(downtime_end),
                                    "component": component,
                                    "reason": f"{component} downtime detected - Status: {downtime_start_metrics['status']} (P:{downtime_start_metrics['performance']:.1f}% Q:{downtime_start_metrics['quality']:.1f}%)",
                                    "duration": duration_display,
                                    "type": "preventive" if downtime_start_metrics['status'] == 'Maintenance' else "reactive",
                                    "severity": severity,
                                    "status": "resolved",
                                    "technician": "System Auto-detected",
                                    "notes": f"Detected from machine logs. Performance: {downtime_start_metrics['performance']:.1f}%, Quality: {downtime_start_metrics['quality']:.1f}%, Status: {downtime_start_metrics['status']}",
                                    "ongoing": False
                                }
                                events.append(event)
                                logger.info(f"✅ Created downtime event: {component} - {duration_display} min")
                    
                    # Handle ongoing downtime
                    if in_downtime and downtime_start:
                        from datetime import datetime
                        downtime_end = datetime.now()
                        duration = self._calculate_duration(downtime_start, downtime_end)
                        
                        event = {
                            "id": f"DT-ONGOING",
                            "timestamp": downtime_start.isoformat() if hasattr(downtime_start, 'isoformat') else str(downtime_start),
                            "end_timestamp": downtime_end.isoformat(),
                            "component": "Multiple",
                            "reason": "Ongoing downtime - system still degraded",
                            "duration": duration,
                            "type": "reactive",
                            "severity": "high",
                            "status": "ongoing",
                            "technician": "Pending",
                            "notes": "Downtime is currently ongoing. Waiting for resolution.",
                            "ongoing": True
                        }
                        events.append(event)
                    
                    # Sort by timestamp descending
                    events.sort(key=lambda x: x['timestamp'], reverse=True)
                    
                    # Limit results
                    events = events[:limit]
                    
                    logger.info(f"✅ Found {critical_count} critical records, generated {len(events)} downtime events from health/metric analysis")
                    return events
                    
        except Exception as e:
            logger.error(f"Error analyzing health drops: {e}")
            import traceback
            traceback.print_exc()
            return []


# Global downtime service instance
downtime_service = DowntimeService()
