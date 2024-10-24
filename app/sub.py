from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Announcement:
    date: str
    content: str

@dataclass
class SubstitutionEntry:
  date: str
  teacher: str
  lesson: int
  substitute_teacher: Optional[str]
  room: str
  class_group: str
  status: str  # "Substituted" or "Cancelled"
  notes: Optional[str] = None

@dataclass
class RoomChangeEntry:
  date: str
  original_room: str
  new_room: str
  lesson: int
  class_group: str

class SubstitutionParser:
  def __init__(self, html_content: str):
    self.soup = BeautifulSoup(html_content, 'html.parser')
    
  def parse_dates(self) -> List[str]:
    """Extract all dates from the schedule."""
    return [div.text.strip() for div in self.soup.find_all('div', class_='datum')]
  
  def parse_announcements(self) -> List[Announcement]:
    """Parse all announcement entries."""
    announcements = []
    current_date = None
    
    for element in self.soup.find_all(['div']):
        # Update current date when we find a date div
        if 'datum' in element.get('class', []):
            current_date = element.text.strip()
            continue
            
        # Process announcement entries
        if 'hianyzas' in element.get('class', []):
            title_div = element.find('div', class_='tanarcim')
            if not title_div:
                continue
                
            # Check if this is an announcement (no data divs)
            data_divs = element.find_all('div', class_='data')
            if not data_divs:
                announcements.append(Announcement(
                    date=current_date,
                    content=title_div.text.strip()
                ))
    
    return announcements
    
  def parse_substitutions(self) -> List[SubstitutionEntry]:
    """Parse all substitution entries."""
    substitutions = []
    current_date = None
    
    for element in self.soup.find_all(['div']):
      # Update current date when we find a date div
      if 'datum' in element.get('class', []):
        current_date = element.text.strip()
        continue
        
      # Process substitution entries
      if 'hianyzas' in element.get('class', []):
        teacher_div = element.find('div', class_='tanarcim')
        if not teacher_div:
          continue
          
        teacher = teacher_div.text.strip()
        
        # Process each substitution data entry
        for data in element.find_all('div', class_='data'):
          lesson = data.find('div', class_='ora').text.strip() if data.find('div', class_='ora') else ''
          substitute = data.find('div', class_='helytan').text.strip() if data.find('div', class_='helytan') else '-'
          room = data.find('div', class_='terem').text.strip() if data.find('div', class_='terem') else ''
          class_group = data.find('div', class_='osztaly').text.strip() if data.find('div', class_='osztaly') else ''
          
          # Get any additional notes
          notes = None
          additional_data = data.find_all('div', class_='subdata')
          if len(additional_data) == 5:
            notes = additional_data[4].text.strip()

          status = "Cancelled" if room.strip() == "Elmarad" else "Substituted"
          
          substitutions.append(SubstitutionEntry(
            date=current_date,
            teacher=teacher,
            lesson=int(lesson.split(".")[0]) if lesson else -1,
            substitute_teacher=substitute if substitute != '-' else None,
            room=room,
            class_group=class_group,
            status=status,
            notes=notes
          ))
    
    return substitutions
  
  def parse_room_changes(self) -> List[RoomChangeEntry]:
    """Parse all room change entries."""
    room_changes = []
    current_date = None
    
    # Find the teremcserék (room changes) section
    for element in self.soup.find_all(['div']):
      if 'datum' in element.get('class', []):
        current_date = element.text.strip()
      
      if 'teremcserekcim' in element.get('class', []):
        # Process room changes after this header
        for change in element.find_next_siblings('div'):
          # we reached the next date, stop processing
          if 'datum' in change.get('class', []):
            break
            
          data = change.find('div', class_='data')
          if not data:
            continue
            
          subdatas = data.find_all('div', class_='subdata')
          try:
            if len(subdatas) >= 4:
              room_changes.append(RoomChangeEntry(
                date=current_date,
                original_room=subdatas[0].text.strip(),
                new_room=subdatas[1].text.strip(),
                lesson=int(subdatas[2].text.strip().split(".")[0]),
                class_group=subdatas[3].text.strip()
              ))
          except:
            print(subdatas)
    
    return room_changes

  def get_summary(self) -> dict:
    """Generate a summary of the substitutions, room changes, and announcements."""
    substitutions = self.parse_substitutions()
    room_changes = self.parse_room_changes()
    announcements = self.parse_announcements()
    
    return {
      'total_substitutions': len(substitutions),
      'cancelled_lessons': len([s for s in substitutions if s.status == "Cancelled"]),
      'substituted_lessons': len([s for s in substitutions if s.status == "Substituted"]),
      'total_room_changes': len(room_changes),
      'total_announcements': len(announcements),
      'affected_classes': len(set(s.class_group for s in substitutions)),
      'affected_teachers': len(set(s.teacher for s in substitutions)),
      'dates': self.parse_dates()
    }

# Example usage
def parse_schedule(html_content: str) -> tuple[List[SubstitutionEntry], List[RoomChangeEntry], List[Announcement], dict]:
  parser = SubstitutionParser(html_content)
  substitutions = parser.parse_substitutions()
  room_changes = parser.parse_room_changes()
  announcements = parser.parse_announcements()
  summary = parser.get_summary()
  return substitutions, room_changes, announcements, summary