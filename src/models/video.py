from datetime import datetime
from src.database import Database

class Video:
    def __init__(self, video_id=None, title=None, cloudinary_url=None, thumbnail=None, file_size=None):
        self.video_id = video_id
        self.title = title
        self.cloudinary_url = cloudinary_url
        self.thumbnail = thumbnail
        self.file_size = file_size
        self.collection = Database.get_instance().get_collection('videos')
    
    def save(self):
        video_data = {
            'videoId': self.video_id,
            'title': self.title,
            'cloudinaryUrl': self.cloudinary_url,
            'thumbnail': self.thumbnail,
            'fileSize': self.file_size,
            'createdAt': datetime.now()
        }
        
        result = self.collection.update_one(
            {'videoId': self.video_id},
            {'$set': video_data},
            upsert=True
        )
        
        return result.acknowledged
    
    @classmethod
    def find_by_video_id(cls, video_id):
        collection = Database.get_instance().get_collection('videos')
        video_data = collection.find_one({'videoId': video_id})
        
        if not video_data:
            return None
        
        return cls(
            video_id=video_data.get('videoId'),
            title=video_data.get('title'),
            cloudinary_url=video_data.get('cloudinaryUrl'),
            thumbnail=video_data.get('thumbnail'),
            file_size=video_data.get('fileSize')
        )