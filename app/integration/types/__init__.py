from typing import List, Optional, Any
from pydantic import BaseModel


# ------------------------
# 🟦 ScoreSaber Structures
# ------------------------

class LeaderboardPlayerInfo(BaseModel):
    id: str
    name: str
    profilePicture: str
    country: str
    permissions: int
    badges: Optional[Any] = None
    role: Optional[Any] = None


class ScoreSaberScore(BaseModel):
    id: int
    leaderboardPlayerInfo: LeaderboardPlayerInfo
    rank: int
    baseScore: int
    modifiedScore: int
    pp: float
    weight: float
    modifiers: str
    multiplier: float
    badCuts: int
    missedNotes: int
    maxCombo: int
    fullCombo: bool
    hmd: int
    timeSet: str
    hasReplay: bool
    deviceHmd: Optional[str] = None
    deviceControllerLeft: Optional[str] = None
    deviceControllerRight: Optional[str] = None


class ScoreSaberDifficulty(BaseModel):
    leaderboardId: int
    difficulty: int
    gameMode: str
    difficultyRaw: str


class ScoreSaberLeaderboard(BaseModel):
    id: int
    songHash: str
    songName: str
    songSubName: str
    songAuthorName: str
    levelAuthorName: str
    difficulty: ScoreSaberDifficulty
    maxScore: int
    createdDate: str
    rankedDate: Optional[str]
    qualifiedDate: Optional[str]
    lovedDate: Optional[str]
    ranked: bool
    qualified: bool
    loved: bool
    maxPP: float
    stars: float
    plays: int
    dailyPlays: int
    positiveModifiers: bool
    coverImage: str


class ScoreSaberCommandData(BaseModel):
    score: ScoreSaberScore
    leaderboard: ScoreSaberLeaderboard


class ScoreSaberScoreMessage(BaseModel):
    commandName: str  # sempre "score"
    commandData: ScoreSaberCommandData


# ------------------------
# 🟧 BeatLeader Structures
# ------------------------

class ScoreImprovement(BaseModel):
    id: int
    timeset: str
    score: int
    accuracy: float
    pp: float
    bonusPp: float
    rank: int
    accRight: float
    accLeft: float
    averageRankedAccuracy: float
    totalPp: float
    totalRank: float
    badCuts: int
    missedNotes: int
    bombCuts: int
    wallsHit: int
    pauses: int
    modifiers: str


class ContextExtension(BaseModel):
    id: int
    playerId: str
    weight: float
    rank: int
    baseScore: int
    modifiedScore: int
    accuracy: float
    pp: float
    passPP: float
    accPP: float
    techPP: float
    bonusPp: float
    modifiers: str
    context: int
    scoreImprovement: Optional[ScoreImprovement] = None


class ModifierValues(BaseModel):
    modifierId: int
    da: float
    fs: float
    sf: float
    ss: float
    gn: float
    na: float
    nb: float
    nf: float
    no: float
    pm: float
    sc: float
    sa: float
    op: float
    ez: float
    hd: float
    smc: float
    ohp: float


class BeatLeaderDifficulty(BaseModel):
    id: int
    value: int
    mode: int
    difficultyName: str
    modeName: str
    status: int
    modifierValues: ModifierValues
    modifiersRating: Optional[Any]
    nominatedTime: int
    qualifiedTime: int
    rankedTime: int
    speedTags: int
    styleTags: int
    featureTags: int
    stars: Optional[float]
    predictedAcc: Optional[float]
    passRating: Optional[float]
    accRating: Optional[float]
    techRating: Optional[float]
    type: int
    njs: float
    nps: float
    notes: int
    bombs: int
    walls: int
    maxScore: int
    duration: Optional[float]
    requirements: int


class BeatLeaderSong(BaseModel):
    id: str
    hash: str
    name: str
    subName: Optional[str] = ""
    author: str
    mapper: str
    mapperId: int
    collaboratorIds: Optional[Any] = None
    coverImage: str
    bpm: float
    duration: Optional[float]
    fullCoverImage: Optional[str] = None
    explicity: int


class BeatLeaderLeaderboard(BaseModel):
    id: str
    song: Optional[BeatLeaderSong] = None
    difficulty: Optional[BeatLeaderDifficulty] = None


class ProfileSettings(BaseModel):
    id: int
    bio: Optional[str]
    message: Optional[str]
    effectName: str
    profileAppearance: str
    hue: Optional[Any] = None
    saturation: Optional[Any] = None
    leftSaberColor: Optional[str]
    rightSaberColor: Optional[str]
    profileCover: Optional[str] = None
    starredFriends: str
    horizontalRichBio: bool
    rankedMapperSort: Optional[str] = None
    showBots: bool
    showAllRatings: bool
    showExplicitCovers: bool
    showStatsPublic: bool
    showStatsPublicPinned: bool


class Player(BaseModel):
    id: str
    name: str
    platform: str
    avatar: str
    country: str
    alias: Optional[str]
    bot: bool
    pp: float
    rank: int
    countryRank: int
    level: int
    experience: int
    prestige: int
    role: Optional[str]
    socials: Optional[Any]
    contextExtensions: Optional[Any]
    patreonFeatures: Optional[Any]
    profileSettings: Optional[ProfileSettings] = None
    clanOrder: str
    clans: List[Any]


class Offsets(BaseModel):
    id: int
    frames: int
    notes: int
    walls: int
    heights: int
    pauses: int
    saberOffsets: int
    customData: int


class BeatLeaderScoreMessage(BaseModel):
    contextExtensions: Optional[List[ContextExtension]]
    myScore: Optional[Any]
    validContexts: int
    experience: int
    leaderboard: BeatLeaderLeaderboard
    accLeft: float
    accRight: float
    id: int
    baseScore: int
    modifiedScore: int
    accuracy: float
    playerId: str
    pp: float
    bonusPp: float
    passPP: float
    accPP: float
    techPP: float
    rank: int
    responseRank: int
    country: str
    fcAccuracy: float
    fcPp: float
    weight: float
    replay: str
    modifiers: str
    badCuts: int
    missedNotes: int
    bombCuts: int
    wallsHit: int
    pauses: int
    fullCombo: bool
    platform: str
    maxCombo: int
    maxStreak: Optional[int]
    hmd: int
    controller: int
    leaderboardId: str
    timeset: str
    timepost: int
    replaysWatched: int
    playCount: int
    lastTryTime: int
    priority: int
    originalId: int
    player: Player
    scoreImprovement: Optional[ScoreImprovement] = None
    rankVoting: Optional[Any]
    metadata: Optional[Any]
    offsets: Offsets
