from typing import List, Tuple, Dict
import logging
from app.models.calibration import CameraCalibration, ParkingRow
from app.models.empty_space import EmptySpace, DetectionWithRow, ParkingAnalysis
from app.models.detection import BoundingBox

logger = logging.getLogger(__name__)

class EmptySpaceDetector:
    """Service for detecting empty parking spaces"""
    
    def __init__(self, calibration: CameraCalibration):
        self.calibration = calibration
        self.rows = sorted(calibration.rows, key=lambda r: r.row_index)
    
    def assign_to_row(self, bbox: BoundingBox) -> Tuple[int, int]:
        """
        Assign bounding box to parking row if it INTERSECTS with the row line
        AND is within the row's X boundaries (yellow lines)
        
        Conditions:
        1. Row line passes through bounding box: bbox.y1 <= row_y <= bbox.y2
        2. Motor center X is within row boundaries: start_x <= center_x <= end_x
        
        Args:
            bbox: Bounding box to assign
            
        Returns: (row_index, row_y_coordinate) or (-1, -1) if no intersection or outside boundaries
        
        Raises: ValueError if no rows are configured
        """
        if not self.rows:
            raise ValueError("No parking rows configured in calibration")
        
        # Validate bounding box coordinates
        if bbox.y1 < 0 or bbox.y2 < 0 or bbox.y1 >= bbox.y2:
            logger.warning(f"Invalid bounding box coordinates: y1={bbox.y1}, y2={bbox.y2}")
            return -1, -1
        
        # Calculate motor center X
        bbox_center_x = (bbox.x1 + bbox.x2) / 2
        
        # Find all rows that intersect with this bounding box
        intersecting_rows = []
        for row in self.rows:
            # Check Y intersection
            if not (bbox.y1 <= row.y_coordinate <= bbox.y2):
                continue
            
            # Check X boundaries (yellow lines)
            row_start_x = row.start_x if row.start_x is not None else self.calibration.row_start_x
            row_end_x = row.end_x if row.end_x is not None else self.calibration.row_end_x
            
            if row_start_x <= bbox_center_x <= row_end_x:
                intersecting_rows.append(row)
            else:
                logger.debug(f"Motor at X={bbox_center_x:.0f} outside row {row.row_index} boundaries "
                           f"(X={row_start_x}-{row_end_x})")
        
        if not intersecting_rows:
            # No intersection with any row or outside all boundaries
            logger.debug(f"Motor at Y={bbox.y1}-{bbox.y2}, X={bbox_center_x:.0f} "
                        f"does not intersect with any row line or is outside boundaries")
            return -1, -1
        
        # If multiple rows intersect (tall motor), choose the one closest to center
        if len(intersecting_rows) > 1:
            bbox_center_y = (bbox.y1 + bbox.y2) / 2
            chosen_row = min(
                intersecting_rows,
                key=lambda r: abs(r.y_coordinate - bbox_center_y)
            )
            logger.debug(f"Motor at Y={bbox.y1}-{bbox.y2} intersects {len(intersecting_rows)} rows, "
                        f"choosing row {chosen_row.row_index}")
        else:
            chosen_row = intersecting_rows[0]
        
        return chosen_row.row_index, chosen_row.y_coordinate
    
    def calculate_expected_space(self, row_index: int) -> float:
        """
        Calculate expected minimum space width for a row with perspective correction
        Formula: min_space_width * (coefficient ^ row_index)
        
        Perspective logic (ROW NUMBERING FROM BOTTOM):
        - Row 0 (bottom/near): Largest space (min_space_width, closest to camera)
        - Row 1, 2, 3... (going up/far): Smaller spaces (more perspective effect)
        
        Returns: Expected space width in pixels
        """
        try:
            if row_index < 0:
                logger.warning(f"Invalid row_index {row_index}, using 0")
                row_index = 0
            
            total_rows = len(self.rows)
            if total_rows == 0:
                logger.warning("No rows configured, using min_space_width")
                return self.calibration.min_space_width
            
            # Row 0 (bottom) = exponent 0 = largest space (min_space_width)
            # Row 1, 2, 3... (going up) = higher exponent = smaller space
            expected_space = self.calibration.min_space_width * (
                self.calibration.space_coefficient ** row_index
            )
            
            # Ensure result is positive and reasonable
            if expected_space <= 0 or expected_space > 10000:
                logger.warning(f"Calculated expected_space {expected_space} is out of range, using min_space_width")
                return self.calibration.min_space_width
            
            return expected_space
        except (OverflowError, ValueError) as e:
            logger.error(f"Error calculating expected space for row {row_index}: {e}")
            return self.calibration.min_space_width
    
    def calculate_row_boundaries(self, row_index: int, detections: List[BoundingBox]) -> Tuple[int, int]:
        """
        Calculate Y boundaries for parking space visualization based on average motor height in this row
        
        Args:
            row_index: Row index
            detections: List of motor detections in this row
            
        Returns: (y1, y2) - top and bottom boundaries based on average motor height
        """
        try:
            # Validate row_index
            if row_index < 0 or row_index >= len(self.rows):
                logger.warning(f"Invalid row_index {row_index}, using first row")
                row_index = 0
            
            row = self.rows[row_index]
            y_center = row.y_coordinate
            
            # Calculate average motor height from detections in this row
            if detections and len(detections) > 0:
                total_height = sum(det.y2 - det.y1 for det in detections)
                avg_height = total_height / len(detections)
                half_height = avg_height / 2
                
                logger.debug(f"Row {row_index}: {len(detections)} motors, avg height={avg_height:.1f}px")
            else:
                # No motors in row, use default height
                half_height = 50
                logger.debug(f"Row {row_index}: No motors, using default height=100px")
            
            # Set boundaries based on average motor height
            y1 = max(0, int(y_center - half_height))
            y2 = int(y_center + half_height)
            
            return y1, y2
        except Exception as e:
            logger.error(f"Error calculating row boundaries for row {row_index}: {e}")
            # Return default boundaries
            return 0, 100
    
    def get_row_x_boundaries(self, row_index: int) -> tuple[int, int]:
        """
        Get X boundaries for a specific row
        Uses per-row boundaries if set, otherwise falls back to global boundaries
        """
        if row_index < 0 or row_index >= len(self.rows):
            return self.calibration.row_start_x, self.calibration.row_end_x
        
        row = self.rows[row_index]
        start_x = row.start_x if row.start_x is not None else self.calibration.row_start_x
        end_x = row.end_x if row.end_x is not None else self.calibration.row_end_x
        
        return start_x, end_x
    
    def detect_empty_spaces_in_row(
        self,
        detections: List[BoundingBox],
        row_index: int
    ) -> List[EmptySpace]:
        """
        Detect empty spaces between motorcycles in a single row
        Handles edge cases:
        - Empty row (no motorcycles)
        - Single motorcycle (no gaps between)
        - Invalid detections
        - Per-row X boundaries for perspective correction
        """
        try:
            # Get row-specific X boundaries
            row_start_x, row_end_x = self.get_row_x_boundaries(row_index)
            
            # Edge case: No motorcycles in row - entire row is empty
            if not detections:
                y1, y2 = self.calculate_row_boundaries(row_index, [])
                width = row_end_x - row_start_x
                expected_space = self.calculate_expected_space(row_index)
                
                logger.debug(f"Row {row_index} is empty, creating full-row empty space")
                
                # Calculate how many motorcycles can fit
                capacity = int(width / expected_space) if expected_space > 0 else 0
                
                return [EmptySpace(
                    space_id=f"row{row_index}_full",
                    row_index=row_index,
                    x1=row_start_x,
                    x2=row_end_x,
                    y1=y1,
                    y2=y2,
                    width=width,
                    can_fit_motorcycle=width >= expected_space,
                    motorcycle_capacity=capacity
                )]
            
            # Edge case: Single motorcycle - check spaces before and after only
            if len(detections) == 1:
                logger.debug(f"Row {row_index} has single motorcycle, checking edge spaces only")
            
            # Filter out invalid detections
            valid_detections = [
                d for d in detections 
                if d.x1 >= 0 and d.x2 > d.x1 and d.y1 >= 0 and d.y2 > d.y1
            ]
            
            if not valid_detections:
                logger.warning(f"Row {row_index} has no valid detections after filtering")
                return []
            
            # Sort detections by X coordinate
            sorted_detections = sorted(valid_detections, key=lambda d: d.x1)
            empty_spaces = []
            expected_space = self.calculate_expected_space(row_index)
            y1, y2 = self.calculate_row_boundaries(row_index, sorted_detections)
            
            # Check space before first motorcycle
            first_motor = sorted_detections[0]
            if first_motor.x1 - row_start_x >= expected_space:
                width = first_motor.x1 - row_start_x
                capacity = int(width / expected_space) if expected_space > 0 else 0
                empty_spaces.append(EmptySpace(
                    space_id=f"row{row_index}_start",
                    row_index=row_index,
                    x1=row_start_x,
                    x2=int(first_motor.x1),
                    y1=y1,
                    y2=y2,
                    width=width,
                    can_fit_motorcycle=True,
                    motorcycle_capacity=capacity
                ))
        
            # Check spaces between motorcycles (only if more than one motorcycle)
            for i in range(len(sorted_detections) - 1):
                try:
                    left_motor = sorted_detections[i]
                    right_motor = sorted_detections[i + 1]
                    
                    gap_x1 = int(left_motor.x2)
                    gap_x2 = int(right_motor.x1)
                    gap_width = gap_x2 - gap_x1
                    
                    # Validate gap width is positive
                    if gap_width < 0:
                        logger.warning(f"Negative gap width detected in row {row_index}: {gap_width}. Motorcycles may be overlapping.")
                        continue
                    
                    if gap_width >= expected_space:
                        capacity = int(gap_width / expected_space) if expected_space > 0 else 0
                        empty_spaces.append(EmptySpace(
                            space_id=f"row{row_index}_space{i}",
                            row_index=row_index,
                            x1=gap_x1,
                            x2=gap_x2,
                            y1=y1,
                            y2=y2,
                            width=gap_width,
                            can_fit_motorcycle=True,
                            motorcycle_capacity=capacity
                        ))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error calculating gap in row {row_index} at position {i}: {e}")
                    continue
        
            # Check space after last motorcycle
            last_motor = sorted_detections[-1]
            if row_end_x - last_motor.x2 >= expected_space:
                width = row_end_x - last_motor.x2
                capacity = int(width / expected_space) if expected_space > 0 else 0
                empty_spaces.append(EmptySpace(
                    space_id=f"row{row_index}_end",
                    row_index=row_index,
                    x1=int(last_motor.x2),
                    x2=row_end_x,
                    y1=y1,
                    y2=y2,
                    width=width,
                    can_fit_motorcycle=True,
                    motorcycle_capacity=capacity
                ))
            
            return empty_spaces
            
        except Exception as e:
            logger.error(f"Unexpected error detecting empty spaces in row {row_index}: {e}")
            return []
    
    def process_detections(
        self,
        detections: List[BoundingBox],
        session_id: str
    ) -> ParkingAnalysis:
        """
        Main processing function to detect empty spaces
        Handles edge cases and errors gracefully
        """
        try:
            # Assign detections to rows
            detections_with_rows = []
            detections_by_row: Dict[int, List[BoundingBox]] = {}
            
            for det in detections:
                try:
                    row_index, row_y = self.assign_to_row(det)
                    
                    # Skip motor if not within tolerance of any row
                    if row_index == -1:
                        logger.debug(f"Skipping motor at Y={det.y1}-{det.y2} (not within tolerance of any row)")
                        continue
                    
                    detections_with_rows.append(DetectionWithRow(
                        bbox={
                            "x1": det.x1,
                            "y1": det.y1,
                            "x2": det.x2,
                            "y2": det.y2
                        },
                        confidence=det.confidence,
                        class_name=det.class_name,
                        assigned_row=row_index,
                        row_y_coordinate=row_y
                    ))
                    
                    if row_index not in detections_by_row:
                        detections_by_row[row_index] = []
                    detections_by_row[row_index].append(det)
                except Exception as e:
                    logger.warning(f"Error assigning detection to row: {e}. Skipping detection.")
                    continue
        
            # Detect empty spaces in each row
            all_empty_spaces = []
            empty_spaces_per_row = {}
            
            for row in self.rows:
                try:
                    row_detections = detections_by_row.get(row.row_index, [])
                    row_empty_spaces = self.detect_empty_spaces_in_row(
                        row_detections,
                        row.row_index
                    )
                    all_empty_spaces.extend(row_empty_spaces)
                    empty_spaces_per_row[row.row_index] = len(row_empty_spaces)
                except Exception as e:
                    logger.error(f"Error detecting empty spaces in row {row.row_index}: {e}")
                    empty_spaces_per_row[row.row_index] = 0
                    continue
            
            # Calculate occupancy metrics
            total_motorcycles = len(detections_with_rows)
            total_empty_spaces = len(all_empty_spaces)
            total_spaces = total_motorcycles + total_empty_spaces
            
            # Handle division by zero
            if total_spaces > 0:
                occupancy_rate = (total_motorcycles / total_spaces * 100)
            else:
                logger.warning("No spaces detected (motorcycles + empty spaces = 0)")
                occupancy_rate = 0.0
            
            return ParkingAnalysis(
                session_id=session_id,
                camera_id=self.calibration.camera_id,
                detections=detections_with_rows,
                empty_spaces=all_empty_spaces,
                total_motorcycles=total_motorcycles,
                total_empty_spaces=total_empty_spaces,
                empty_spaces_per_row=empty_spaces_per_row,
                parking_occupancy_rate=round(occupancy_rate, 2)
            )
        
        except Exception as e:
            logger.error(f"Critical error in process_detections: {e}")
            # Return minimal valid analysis
            return ParkingAnalysis(
                session_id=session_id,
                camera_id=self.calibration.camera_id,
                detections=[],
                empty_spaces=[],
                total_motorcycles=0,
                total_empty_spaces=0,
                empty_spaces_per_row={},
                parking_occupancy_rate=0.0
            )
