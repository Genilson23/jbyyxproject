# -*- coding: utf-8 -*-

#   This file is part of moose.
#
#    Moose is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Moose is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with moose; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import wx, random, sys, wx.html, wx.richtext, os, webbrowser, re
import network, engine, packets, keyhandler, dialogs
from deck import Deck
from ctypes import *

POS_FIELD = 0
POS_HAND = 1
POS_DECK = 2
POS_GRAVE = 3
POS_SIDEDECK = 4
POS_FUSIONDECK = 5
POS_RFG = 6
POS_OPP_FIELD = 7
POS_OPP_HAND = 8
POS_OPP_GRAVE = 9
POS_OPP_RFG = 10
POS_OPP_DECK = 11
POS_OPP_SIDEDECK = 12
POS_OPP_FUSIONDECK = 13
POS_STACK_1 = 14
POS_STACK_2 = 15
POS_STACK_3 = 16
POS_STACK_4 = 17
POS_STACK_5 = 18
POS_OPP_STACK_1 = 19
POS_OPP_STACK_2 = 20
POS_OPP_STACK_3 = 21
POS_OPP_STACK_4 = 22
POS_OPP_STACK_5 = 23

FACE_DOWN = 0
FACE_UP = 1

CARD_VERTICAL = 0
CARD_HORIZONTAL = 1

CHAT_GAME = 0
CHAT_PLAYER = 1
CHAT_OPPONENT = 2
CHAT_CONSOLE = 3

LOOK_DECK_YES = 0
LOOK_DECK_NO = 1
LOOK_GRAVE_YES = 2
LOOK_GRAVE_NO = 3
LOOK_RFG_YES = 4
LOOK_RFG_NO = 5
LOOK_FUSIONDECK_YES = 6
LOOK_FUSIONDECK_NO = 7
LOOK_OPPONENT_GRAVE_YES = 8
LOOK_OPPONENT_GRAVE_NO = 9
LOOK_OPPONENT_RFG_YES = 10
LOOK_OPPONENT_RFG_NO = 11
LOOK_SIDEDECK_YES = 12
LOOK_SIDEDECK_NO = 13
LOOK_STACK_1_YES = 14
LOOK_STACK_1_NO = 15
LOOK_STACK_2_YES = 16
LOOK_STACK_2_NO = 17
LOOK_STACK_3_YES = 18
LOOK_STACK_3_NO = 19
LOOK_STACK_4_YES = 20
LOOK_STACK_4_NO = 21
LOOK_STACK_5_YES = 22
LOOK_STACK_5_NO = 23
LOOK_OPP_STACK_1_YES = 24
LOOK_OPP_STACK_1_NO = 25
LOOK_OPP_STACK_2_YES = 26
LOOK_OPP_STACK_2_NO = 27
LOOK_OPP_STACK_3_YES = 28
LOOK_OPP_STACK_3_NO = 29
LOOK_OPP_STACK_4_YES = 30
LOOK_OPP_STACK_4_NO = 31
LOOK_OPP_STACK_5_YES = 32
LOOK_OPP_STACK_5_NO = 33

ACTION_DISCARDTOP = 0
ACTION_REVEALTOP = 1


class GameObject(wx.Window):
    def __init__(self, parent, pos, texture, size=-1):
        self._texture = texture
        if size == -1:
            size = (self._texture.GetWidth(), self._texture.GetHeight())
        wx.Window.__init__(self, parent=parent, id=-1, pos=pos, size=size)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self._texture, 0, 0, True)

    def SetTexture(self, texture):
        self._texture = texture
        self.Refresh()
        

class ConsoleCtrl(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, pos=(130,347), size=(185,-1), style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnPressEnter)

    def OnPressEnter(self, event):
        if len(self.GetValue()) < 1:
            return
        m = self.GetValue()
        self.SetValue('')
        self.Parent.ProcessMessage(m)

class GamePanel(wx.Panel):
    def __init__(self, parent, engine):
        wx.Panel.__init__(self, parent)
        self._engine = engine
        self._noneparent = wx.Panel(self,-1,(0,0),(0,0))
        self._noneparent.Hide()
        self._nick = ''
        self._opponentnick = ''
        self._origdeck = None
        self._sidedeck = []
        self._fusiondeck = []
        self._field = []
        self._deck = []
        self._grave = []
        self._rfg = []
        self._hand = []
        self._consolectrl = ConsoleCtrl(self)
        #stacks
        self._stack1 = []
        self._stack2 = []
        self._stack3 = []
        self._stack4 = []
        self._stack5 = []
        # Menu
        self._menu = wx.MenuBar()
        
        self._menufile = wx.Menu()
        item = wx.MenuItem(self._menufile,-1,self._engine.GetLangString('Reset Game/Side'))
        item.SetBitmap(self._engine.GetSkinImage('Reload'))
        self.Parent.Bind(wx.EVT_MENU, self.OnGamePopupResetGame, item)
        self._menufile.AppendItem(item)
        item = wx.MenuItem(self._menufile,-1,self._engine.GetLangString('Close'))
        item.SetBitmap(self._engine.GetSkinImage('Close'))
        self.Parent.Bind(wx.EVT_MENU, self.Parent.OnExit, item)
        self._menufile.AppendItem(item)
        self._menu.Append(self._menufile, self._engine.GetLangString('File'))
        
        self._menuactions = wx.Menu()
        item = wx.MenuItem(self._menuactions,-1,self._engine.GetLangString('Graveyard'))
        item.SetBitmap(self._engine.GetSkinImage('Graveico'))
        self.Parent.Bind(wx.EVT_MENU, self.OnGraveLClick, item)
        self._menuactions.AppendItem(item)
        item = wx.MenuItem(self._menuactions,-1,self._engine.GetLangString('Removed From Game'))
        item.SetBitmap(self._engine.GetSkinImage('Torfg'))
        self.Parent.Bind(wx.EVT_MENU, self.OnGamePopupRFG, item)
        self._menuactions.AppendItem(item)
        item = wx.MenuItem(self._menuactions,-1,self._engine.GetLangString('Search Deck'))
        self.Parent.Bind(wx.EVT_MENU, self.OnPopupDeckSearch, item)
        item.SetBitmap(self._engine.GetSkinImage('Searchdeck'))
        self._menuactions.AppendItem(item)
        item = wx.MenuItem(self._menuactions,-1,self._engine.GetLangString("Opponent's Grave"))
        item.SetBitmap(self._engine.GetSkinImage('Tograve'))
        self.Parent.Bind(wx.EVT_MENU, self.OnOpponentGraveLClick, item)
        self._menuactions.AppendItem(item)
        item = wx.MenuItem(self._menuactions,-1,self._engine.GetLangString("Opponent's RFG"))
        item.SetBitmap(self._engine.GetSkinImage('Torfg'))
        self.Parent.Bind(wx.EVT_MENU, self.OnGamePopupOpponentRFG, item)
        self._menuactions.AppendItem(item)
        item = wx.MenuItem(self._menuactions,-1,self._engine.GetLangString('Extra Deck'))
        item.SetBitmap(self._engine.GetSkinImage('Toextra'))
        self.Parent.Bind(wx.EVT_MENU, self.OnGamePopupFusionDeck, item)
        self._menuactions.AppendItem(item)
        #item = wx.MenuItem(self._menuactions,-1,self._engine.GetLangString('Side Deck'))
        #item.SetBitmap(self._engine.GetSkinImage('Toextra'))
        #self.Parent.Bind(wx.EVT_MENU, self.OnGamePopupSideDeck, item)
        #self._menuactions.AppendItem(item)
        item = wx.MenuItem(self._menuactions,-1,self._engine.GetLangString('Roll a D6'))
        item.SetBitmap(self._engine.GetSkinImage('Luck'))
        self.Parent.Bind(wx.EVT_MENU, self.RollD6, item)
        self._menuactions.AppendItem(item)
        item = wx.MenuItem(self._menuactions,-1,self._engine.GetLangString('Flip a Coin'))
        item.SetBitmap(self._engine.GetSkinImage('Luck'))
        self.Parent.Bind(wx.EVT_MENU, self.FlipCoin, item)
        self._menuactions.AppendItem(item)
        self._menu.Append(self._menuactions, self._engine.GetLangString('Actions'))
        
        self._menuhelp = wx.Menu()
        item = wx.MenuItem(self._menuhelp,-1,self._engine.GetLangString('Preferences'))
        item.SetBitmap(self._engine.GetSkinImage('Preferences'))
        self.Parent.Bind(wx.EVT_MENU, self.OnMenuSettings, item)
        self._menuhelp.AppendItem(item)
        item = wx.MenuItem(self._menuhelp,-1,self._engine.GetLangString('Smiles'))
        item.SetBitmap(self._engine.GetSkinImage('Smile'))
        self.Parent.Bind(wx.EVT_MENU, self.OnMenuSmiles, item)
        self._menuhelp.AppendItem(item)
        item = wx.MenuItem(self._menuhelp,-1,self._engine.GetLangString('J_PROJECT.Web'))
        item.SetBitmap(self._engine.GetSkinImage('Web'))
        self.Parent.Bind(wx.EVT_MENU, self.OnMenuWeb, item)
        self._menuhelp.AppendItem(item)
        #item = wx.MenuItem(self._menuhelp,-1,self._engine.GetLangString('About'))
        #item.SetBitmap(self._engine.GetSkinImage('About'))
        #self.Parent.Bind(wx.EVT_MENU, self.OnMenuAbout, item)
        #self._menuhelp.AppendItem(item)
        self._menu.Append(self._menuhelp, self._engine.GetLangString('Help'))
        self.Parent.SetMenuBar(self._menu)

        # Message
        #self._messagectrl = wx.html.HtmlWindow(self, pos=(703,370), size=(154,330))
        #self._messagectrl.SetFonts('Tahoma','Tahoma',[8,8,8,8,8,8,8])
        #self._messagetext = ''
        self._messagectrl = wx.richtext.RichTextCtrl(self, pos=(703,440), size=(254,310), style=wx.richtext.RE_MULTILINE|wx.richtext.RE_READONLY|wx.NO_BORDER)
        self._messagectrl.BeginFont(wx.Font(pointSize=8,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL, faceName="Serpentine-Light"))
        # Smiles
        #self._smiles = ['angel','angry','asd','baby','bana','bhua','biggrin','biglaugha','coffee','censored','byebye','confused','deer','disgust','eek','elf1','elf2','elf3','flamed1','flamed2','freddy','frown','frusta','ghgh','girl','goccia','guns','hammer','hippy','ghgh2','rofl','glass','blush','king','kiss','laugh','lingua','lol','lolly','look','love','mad','metal','ass','nono','no','o','oink','omg','ahsi','laughs','up','down','puke','rain','read','woot','rofl','roll','rolly','rosik','rotfl','sad','saint','sbang','sbav','scratch','ass2','ser','shocked','sigh','silly','smile','smoke','smokin','sheep','spiny','study','sure','talk','tongue','sad2','ueee','wave','woot','yuppi','zzz','afraid']
        self._smiles = ['angel','baby','X','S','D','deer','disgust','down','elf','flame','(','girl','goccia','hippy','king','kiss','laughs','lingua','look','love','mad','metal','no','nu','O','oink','omg','rain','sad','saint','I',')','sheep','shocked','sigh','silly','smoke','smokin','sure','P','up','wave','zzz']
        # Console
        self._consolectrl.SetFont(wx.Font(pointSize=8,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL, faceName="Tahoma"))
        self._consolectrl.SetFocus()
        self._gravelistctrl = GraveListControl(self)
        #stacks
        self._stack_1_listctrl = Stack_1_ListControl(self)
        self._stack_2_listctrl = Stack_2_ListControl(self)
        self._stack_3_listctrl = Stack_3_ListControl(self)
        self._stack_4_listctrl = Stack_4_ListControl(self)
        self._stack_5_listctrl = Stack_5_ListControl(self)
        
        #self._oppstack_1_listctrl = OppStack_1_ListControl(self)
        #self._oppstack_2_listctrl = OppStack_2_ListControl(self)
        #self._oppstack_3_listctrl = OppStack_3_ListControl(self)
        #self._oppstack_4_listctrl = OppStack_4_ListControl(self)
        #self._oppstack_5_listctrl = OppStack_5_ListControl(self)
        
        self._decklistctrl = DeckListControl(self)
        self._rfglistctrl = RFGListControl(self)
        self._opponentgravelistctrl = OpponentGraveListControl(self)
        self._opponentdecklistctrl = OpponentDeckListControl(self)
        self._opponentrfglistctrl = OpponentRFGListControl(self)
        self._fusiondecklistctrl = FusionDeckListControl(self)
        self._sidedecklistctrl = SideDeckListControl(self)
        self._opponentfusiondecklistctrl = OpponentFusionDeckListControl(self)
        self._opponentsidedecklistctrl = OpponentSideDeckListControl(self)
        self._cmdhandlers = {}
        self._cardsize=wx.Size(62,88)
        self.CommandHandlers()
        #self._oppstack1 = []
        #self._oppstack2 = []
        #self._oppstack3 = []
        #self._oppstack4 = []
        #self._oppstack5 = []
        self._opponentorigdeck = None
        self._opponentfield = []
        self._opponentdeck = []
        self._opponentgrave = []
        self._opponentrfg = []
        self._opponenthand = []
        self._opponentsidedeck = []
        self._opponentfusiondeck = []
        self._notes = []
        self._serial = 0
        self._opponentserial = 0
        # Field
        self._fieldctrl = FieldControl(self)
        self._fieldctrl.Bind(wx.EVT_RIGHT_UP, self.OnFieldLeftUp)
        # OpponentField
        self._opponentfieldctrl = OpponentFieldControl(self)
        # Deck
        self._deckctrl = DeckControl(self._fieldctrl, (619,206), self._engine.GetSkinImage('Deck'))
        self._deckctrl.Bind(wx.EVT_LEFT_DCLICK, self.OnDeckDClick)
        self._deckctrl.Bind(wx.EVT_RIGHT_UP, self.OnDeckRClick)
        self._deckcounttext = wx.StaticText(self._fieldctrl, -1, '0', pos=(640,230))
        # FusionDeck
        self._fusiondeckctrl = FusionDeckControl(self._fieldctrl, (20,166), self._engine.GetSkinImage('FusionDeck'))
        self._fusiondeckctrl.Bind(wx.EVT_LEFT_UP, self.OnGamePopupFusionDeck)
        self._extradeckcounttext = wx.StaticText(self._fieldctrl, -1, '0', pos=(41,190))
        self._oppextradeckcounttext = wx.StaticText(self._opponentfieldctrl, -1, '0', pos=(640,60))
        # Grave
        self._gravectrl = GraveControl(self._fieldctrl, (619,109), self._engine.GetSkinImage('Grave'), self)
        self._gravectrl.Bind(wx.EVT_LEFT_UP, self.OnGraveLClick)
        self._gravectrl.UpdateCardTooltip(self._grave)
        #Stacks
        self._stack1ctrl = Stack_1_Control(self._fieldctrl, (126,28), self._engine.GetSkinImage('Stack'), self)
        self._stack1ctrl.Bind(wx.EVT_LEFT_UP, self.OnStack_1_LClick)
        self._stack1ctrl.UpdateCardTooltip(self._stack1)
        
        self._stack2ctrl = Stack_2_Control(self._fieldctrl, (223,28), self._engine.GetSkinImage('Stack'), self)
        self._stack2ctrl.Bind(wx.EVT_LEFT_UP, self.OnStack_2_LClick)
        self._stack2ctrl.UpdateCardTooltip(self._stack2)
        
        self._stack3ctrl = Stack_3_Control(self._fieldctrl, (319,28), self._engine.GetSkinImage('Stack'), self)
        self._stack3ctrl.Bind(wx.EVT_LEFT_UP, self.OnStack_3_LClick)
        self._stack3ctrl.UpdateCardTooltip(self._stack3)
        
        self._stack4ctrl = Stack_4_Control(self._fieldctrl, (417,28), self._engine.GetSkinImage('Stack'), self)
        self._stack4ctrl.Bind(wx.EVT_LEFT_UP, self.OnStack_4_LClick)
        self._stack4ctrl.UpdateCardTooltip(self._stack4)
        
        self._stack5ctrl = Stack_5_Control(self._fieldctrl, (515,28), self._engine.GetSkinImage('Stack'), self)
        self._stack5ctrl.Bind(wx.EVT_LEFT_UP, self.OnStack_5_LClick)
        self._stack5ctrl.UpdateCardTooltip(self._stack5)
        
        # RFG
        self._rfgctrl = RFGControl(self._fieldctrl, (619,11), self._engine.GetSkinImage('RFG'), self)
        self._rfgctrl.Bind(wx.EVT_LEFT_UP, self.OnGamePopupRFG)
        self._rfgctrl.UpdateCardTooltip(self._rfg)
        # OpponentGrave
        self._opponentgravectrl = OpponentGraveControl(self._opponentfieldctrl, (20,102), self._engine.GetSkinImage('Grave'), self)
        self._opponentgravectrl.Bind(wx.EVT_LEFT_UP, self.OnOpponentGraveLClick)
        self._opponentgravectrl.UpdateCardTooltip(self._opponentgrave)
        # OpponentRFG
        self._opponentrfgctrl = OpponentRFGControl(self._opponentfieldctrl, (20,202), self._engine.GetSkinImage('RFG'), self)
        self._opponentrfgctrl.Bind(wx.EVT_LEFT_UP, self.OnGamePopupOpponentRFG)
        self._opponentrfgctrl.UpdateCardTooltip(self._opponentrfg)
        # OpponentDeck
        self._opponentdeckctrl = OpponentDeckControl(self._opponentfieldctrl, (20,4), self._engine.GetSkinImage('Deck'))
        self._oppdeckcounttext = wx.StaticText(self._opponentfieldctrl, -1, '0', pos=(41,28))
        # Hand
        self._handctrl = HandControl(self)
        
        self.RefreshHand()
        # OpponentHand
        self._opponenthandctrl = OpponentHandControl(self)
        self.RefreshOpponentHand()
        # Score
        self._scorectrl = ScoreControl(self)
        # Phases
        self._drawphasectrl = DrawPhaseControl(self)
        self._standbyphasectrl = StandbyPhaseControl(self)
        self._mainphase1ctrl = MainPhase1Control(self)
        self._battlephasectrl = BattlePhaseControl(self)
        self._mainphase2ctrl = MainPhase2Control(self)
        self._endphasectrl = EndPhaseControl(self)
        # Menu 1
        self._hand_mt_menu = wx.Menu()
        item = wx.MenuItem(self._hand_mt_menu, -1, self._engine.GetLangString('Activate'))
        item.SetBitmap(self._engine.GetSkinImage('Activate'))
        self._hand_mt_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnHandMTActivate, item)
        item = wx.MenuItem(self._hand_mt_menu, -1, self._engine.GetLangString('Position'))
        item.SetBitmap(self._engine.GetSkinImage('Setst'))
        self._hand_mt_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnHandMTPosition, item)
        # Menu 2
        self._hand_monster_menu = wx.Menu()
        item = wx.MenuItem(self._hand_monster_menu, -1, self._engine.GetLangString('Summon'))
        item.SetBitmap(self._engine.GetSkinImage('Summon'))
        self._hand_monster_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnHandMonsterSummon, item)
        item = wx.MenuItem(self._hand_monster_menu, -1, self._engine.GetLangString('Position'))
        item.SetBitmap(self._engine.GetSkinImage('Set'))
        self._hand_monster_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnHandMonsterPosition, item)
        # Menu 3
        self._game_menu = wx.Menu()
        #item = wx.MenuItem(self._game_menu, -1, 'New Note')
        #self._game_menu.AppendItem(item)
        #self.Bind(wx.EVT_MENU, self.OnNewNote, item)
        item = wx.MenuItem(self._game_menu, -1, self._engine.GetLangString('Graveyard'))
        item.SetBitmap(self._engine.GetSkinImage('Graveico'))
        self._game_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnGraveLClick, item)
        item = wx.MenuItem(self._game_menu, -1, self._engine.GetLangString('Removed From Game'))
        item.SetBitmap(self._engine.GetSkinImage('Torfg'))
        self._game_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnGamePopupRFG, item)
        item = wx.MenuItem(self._game_menu, -1, self._engine.GetLangString('Search Deck'))
        item.SetBitmap(self._engine.GetSkinImage('Searchdeck'))
        self._game_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPopupDeckSearch, item)
        item = wx.MenuItem(self._game_menu, -1, self._engine.GetLangString("Opponent's RFG"))
        item.SetBitmap(self._engine.GetSkinImage('Torfg'))
        self._game_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnGamePopupOpponentRFG, item)
        item = wx.MenuItem(self._game_menu, -1, self._engine.GetLangString('Roll a d6'))
        item.SetBitmap(self._engine.GetSkinImage('Luck'))
        self._game_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPopupRollD6, item)
        item = wx.MenuItem(self._game_menu, -1, self._engine.GetLangString('Flip a Coin'))
        item.SetBitmap(self._engine.GetSkinImage('Luck'))
        self._game_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPopupFlipCoin, item)
        item = wx.MenuItem(self._game_menu, -1, self._engine.GetLangString('Extra Deck'))
        item.SetBitmap(self._engine.GetSkinImage('Toextra'))
        self._game_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnGamePopupFusionDeck, item)
        item = wx.MenuItem(self._game_menu, -1, self._engine.GetLangString('Reset Game/Side'))
        item.SetBitmap(self._engine.GetSkinImage('Reload'))
        self._game_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnGamePopupResetGame, item)
        # Card Visualization
        self._cardnamectrl = wx.StaticText(self, -1, pos=(720,34))
        fontnameg = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, wx.CENTRE, faceName="Serpentine-Light") 
        self._cardnamectrl.SetFont(fontnameg) 
        self._cardimagectrl = wx.StaticBitmap(self, -1, size=(136,200), pos=(762,52))
        self._cardattributectrl = wx.StaticBitmap(self, -1, size=(32,32), pos=(720,122))
        self._cardtypectrl = wx.StaticBitmap(self, -1, size=(32,32), pos=(720,88))
        self._cardtype2ctrl = wx.StaticBitmap(self, -1, size=(32,32), pos=(720,156))
        self._cardstarsctrl = wx.StaticText(self, -1, style=wx.ALIGN_LEFT, pos=(720,52))
        fontname22 = wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD, faceName="Serpentine-Light")
        self._cardstarsctrl.SetFont(fontname22)
        self._carddescriptionctrl = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(254,180), pos=(703,260))
        # Hotkeys
        self._keyhandler = keyhandler.KeyHandler()
        self._hotkeys = {}
        self.LoadHotkeys()
        self._consolectrl.Bind(wx.EVT_KILL_FOCUS, self.OnConsoleLostFocus)
        self._consolectrl.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self._smilesdialog = dialogs.SmilesDialog(self.Parent, self._engine, self._smiles)
        #
        self.UseDeck(self._engine.Deck)

    # Apre il dialogo delle impostazioni
    def OnMenuSettings(self, event=None):
        dialogs.SettingsDialog(self.Parent,self._engine.Frame).ShowModal()

    def OnMenuSmiles(self, event=None):
        if not self._smilesdialog.IsShown():
            self._smilesdialog.Show()

    # Apre il browser predefinito alla homepage di Moose
    def OnMenuWeb(self, event=None):
        try:
            webbrowser.open_new_tab('http://akademija.visiems.lt/')
        except:
            pass

    # Mostra la finestra About
    def OnMenuAbout(self, event = None):
        info = wx.AboutDialogInfo()
        info.SetName(self._engine.GetName())
        info.SetIcon(wx.IconFromLocation(wx.IconLocation(os.path.join(self._engine.BaseDirectory,'mooseduel32x32.ico'))))
        info.SetWebSite('http://mooseproject.blogspot.com/')
        info.SetVersion(self._engine.GetVersion())
        info.SetDescription('Moose is a multi-platform Yu-Gi-Oh! Dueling and Deck Building application written in Python and using wxPython as GUI Library.\n\nLatest Changelog:\n %s' % self._engine.GetChangelog())
        info.SetLicense("""Moose is free software; you can redistribute it and/or modify it 
under the terms of the GNU General Public License as published by the Free Software Foundation; 
either version 2 of the License, or (at your option) any later version.

Moose is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have received a copy of 
the GNU General Public License along with Moose; if not, write to 
the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA""")
        info.AddDeveloper("""Michele 'MaZzo' Mazzoni""")
        info.AddDeveloper("""Andrea 'Coil' Bucciotti""")
        info.AddArtist("""Michele 'MaZzo' Mazzoni""")
        info.AddArtist("""Icons: Alexandre 'sa-ki' Moore
        http://www.iconsdesigns.com/""")
        info.AddArtist("""Card's blanks: http://italianyugioh.forumfree.net/?t=17734912""" )
        wx.AboutBox(info)

    def OnConsoleLostFocus(self, event):
        if self.IsShown() and self.IsShownOnScreen() and not self._decklistctrl.IsActive() and not self._opponentdecklistctrl.IsActive() and not self._gravelistctrl.IsActive() and not self._stack_1_listctrl.IsActive() and not self._stack_2_listctrl.IsActive() and not self._stack_3_listctrl.IsActive() and not self._stack_4_listctrl.IsActive() and not self._stack_5_listctrl.IsActive() and not self._opponentgravelistctrl.IsActive() and not self._rfglistctrl.IsActive() and not self._opponentrfglistctrl.IsActive() and not self._fusiondecklistctrl.IsActive() and not self._sidedecklistctrl.IsActive() and not self._opponentfusiondecklistctrl.IsActive() and not self._opponentsidedecklistctrl.IsActive() and not self._smilesdialog.IsActive():
            self._consolectrl.SetFocus()

    def Pass(self):
        pass

    def GetHotkeyHandler(self, name):
        if self._hotkeys.has_key(name):
            return self._hotkeys[name]
        else:
            return self.Pass

    def LoadHotkeys(self):
        self._hotkeys['Shuffle'] = self.Shuffle
        self._hotkeys['RollD6'] = self.RollD6
        self._hotkeys['Next Phase'] = self.NextPhase
        self._hotkeys['End Turn'] = self.EndTurn
        self._hotkeys['Draw'] = self.OnDeckDraw
        self._hotkeys['Draw and Show'] = self.OnDeckDrawShow
        self._hotkeys['Flip Coin'] = self.FlipCoin
        self._hotkeys['Reset Game'] = self.ResetGame

        hotkeysdict = self._engine.GetAllHotkeys()
        for handler, code in hotkeysdict.items():
            if not code == '':
                self._keyhandler.AddHandler(code, self.GetHotkeyHandler(handler))

    def OnKeyUp(self, event):
        self._keyhandler.OnKeyEvent(event.GetKeyCode(), event.GetModifiers())
        self._consolectrl.SetFocus()

    def ClearPhases(self):
        self._standbyphasectrl._sel = False
        self._standbyphasectrl.Hide()
        self._standbyphasectrl.Show()
        self._drawphasectrl._sel = False
        self._drawphasectrl.Hide()
        self._drawphasectrl.Show()
        self._mainphase1ctrl._sel = False
        self._mainphase1ctrl.Hide()
        self._mainphase1ctrl.Show()
        self._battlephasectrl._sel = False
        self._battlephasectrl.Hide()
        self._battlephasectrl.Show()
        self._mainphase2ctrl._sel = False
        self._mainphase2ctrl.Hide()
        self._mainphase2ctrl.Show()
        self._endphasectrl._sel = False
        self._endphasectrl.Hide()
        self._endphasectrl.Show()
    
    def OnFieldLeftUp(self, event):
        self.PopupMenu(self._game_menu)

    def OnGamePopupRFG(self, event=None):
        if self._rfglistctrl.IsShown():
            self._rfglistctrl.Hide()
            self.WriteLookPacket(LOOK_RFG_NO)
            self.WriteGameMessage(self._engine.GetLangString("end looking at his RFG."), CHAT_PLAYER)
        else:
            self._rfglistctrl.Show()
            self.WriteLookPacket(LOOK_RFG_YES)
            self.WriteGameMessage(self._engine.GetLangString("is looking at his RFG."), CHAT_PLAYER)

    def OnGamePopupOpponentRFG(self, event=None):
        if self._opponentrfglistctrl.IsShown():
            self._opponentrfglistctrl.Hide()
            self.WriteLookPacket(LOOK_OPPONENT_RFG_NO)
            self.WriteGameMessage(self._engine.GetLangString("end looking at his opponent's RFG."), CHAT_PLAYER)
        else:
            self._opponentrfglistctrl.Show()
            self.WriteLookPacket(LOOK_OPPONENT_RFG_YES)
            self.WriteGameMessage(self._engine.GetLangString("is looking at his opponent's RFG."), CHAT_PLAYER)

    def OnGamePopupFusionDeck(self, event=None):
        if self._fusiondecklistctrl.IsShown():
            self._fusiondecklistctrl.Hide()
            self.WriteLookPacket(LOOK_FUSIONDECK_NO)
            self.WriteGameMessage(self._engine.GetLangString("end looking at his Extra Deck."), CHAT_PLAYER)
        else:
            self._fusiondecklistctrl.Show()
            self.WriteLookPacket(LOOK_FUSIONDECK_YES)
            self.WriteGameMessage(self._engine.GetLangString("is looking at his Extra Deck."), CHAT_PLAYER)
    
    def OnGamePopupSideDeck(self, event=None):
        if self._sidedecklistctrl.IsShown():
            self._sidedecklistctrl.Hide()
            self.WriteLookPacket(LOOK_SIDEDECK_NO)
            self.WriteGameMessage(self._engine.GetLangString("end looking at his Side Deck."), CHAT_PLAYER)
        else:
            self._sidedecklistctrl.Show()
            self.WriteLookPacket(LOOK_SIDEDECK_YES)
            self.WriteGameMessage(self._engine.GetLangString("is looking at his Side Deck."), CHAT_PLAYER)

    def OnGamePopupResetGame(self, event=None):
        self.OnGamePopupSideDeck()
        self.ResetGame()
    
    def GetOrigDeck(self):
        return self._origdeck

    def ClearGame(self):
        self._deck = []
        self._sidedeck = []
        self._fusiondeck = []
        self._hand = []
        self._grave = []
        self._stack1 = []
        self._stack2 = []
        self._stack3 = []
        self._stack4 = []
        self._stack5 = []
        self._rfg = []
        self._opponentdeck = []
        self._opponentsidedeck = []
        self._opponentfusiondeck = []
        self._opponenthand = []
        self._opponentgrave = []
        self._opponentrfg = []

    def UseDeck(self, deck):
        self._origdeck = deck
        self.ClearGame()
        deck = self._origdeck.GetGameCards()
        side = self._origdeck.GetSide()
        fusion = self._origdeck.GetFusions()
        for c in deck:
            g = CardControl(self._decklistctrl, c.Duplicate(), self._engine, self, self.NewCardSerial(), cpos=POS_DECK)
            self.AddCardToBottom(self._deck, g)
        for c in side:
            g = CardControl(self._noneparent, c.Duplicate(), self._engine, self, self.NewCardSerial(), cpos=POS_SIDEDECK)
            self.AddCardToBottom(self._sidedeck, g)
        for c in fusion:
            g = CardControl(self._fusiondecklistctrl, c.Duplicate(), self._engine, self, self.NewCardSerial(), cpos=POS_FUSIONDECK)
            self.AddCardToBottom(self._fusiondeck, g)
        self.RefreshDeck()
        self.RefreshHand()
        self.RefreshRFG()
        self.RefreshGrave()
        self.RefreshStack1()
        self.RefreshStack2()
        self.RefreshStack3()
        self.RefreshStack4()
        self.RefreshStack5()
        self.RefreshFusionDeck()
        self.RefreshSideDeck()
        self.RefreshOpponentDeck()
        self.RefreshOpponentHand()
        self.RefreshOpponentRFG()
        self.RefreshOpponentGrave()
        self.RefreshOpponentFusionDeck()
        self.RefreshOpponentSideDeck()
    
    def OnCardTarget(self, event=None):
        card = self._currentcard
        card.Target()
        card.Hide()
        card.Show()
        self.WriteTargetPacket(0, card.GetSerial())

    def OnCardAddCounter(self, event=None):
        card = self._currentcard
        card.AddCounters(1)
        self.WriteGameMessage(' %s %s' % (self._engine.GetLangString("add a counter to"), card.GetCardName()), CHAT_PLAYER)
        self.WriteCardCounterPacket(card.GetSerial(), 0, 1)

    def OnCardRemoveCounter(self, event=None):
        card = self._currentcard
        card.RemoveCounters(1)
        self.WriteGameMessage(' %s %s' % (self._engine.GetLangString("removed a counter from"), card.GetCardName()), CHAT_PLAYER)
        self.WriteCardCounterPacket(card.GetSerial(), 1, 1)
    
    def OnCardChangeControl(self, event=None):
        card = self._currentcard
        self.WriteGameMessage(' %s %s' % (self._engine.GetLangString("changed control..."), card.GetCardName()), CHAT_PLAYER)
        self.WriteChangeControlPacket(card.GetSerial(), 1, 1)

    def OnOpponentCardTarget(self, event=None):
        card = self._opponentcurrentcard
        card.Target()
        card.Hide()
        card.Show()
        self.WriteTargetPacket(1, card.GetSerial())

    def OnCardPopup(self, c):
        pos = c.GetCardPosition()
        if pos == POS_FIELD:
            self.OnCardFieldPopup(c)
        elif pos == POS_HAND:
            self.OnCardHandPopup(c)
        elif pos == POS_GRAVE:
            self.OnCardGravePopup(c)
        elif pos == POS_RFG:
            self.OnCardRFGPopup(c)
        elif pos == POS_DECK:
            self.OnCardDeckPopup(c)
        elif pos == POS_SIDEDECK:
            self.OnCardSideDeckPopup(c)

    def OnCardHandPopup(self, c):
        menu = wx.Menu()
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('Hand Shuffle'))
        item.SetBitmap(self._engine.GetSkinImage('Todecksh'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardShuffleHand, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Grave'))
        item.SetBitmap(self._engine.GetSkinImage('Tograve'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardHandToGrave, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('To RFG'))
        item.SetBitmap(self._engine.GetSkinImage('Torfg'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardHandToRFG, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Deck/Shuffle'))
        item.SetBitmap(self._engine.GetSkinImage('Todecksh'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardHandToDeckShuffle, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Top-Deck'))
        item.SetBitmap(self._engine.GetSkinImage('Totopdeck'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardHandToTopDeck, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Bottom-Deck'))
        item.SetBitmap(self._engine.GetSkinImage('Tobottomdeck'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardHandToBottomDeck, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('Target'))
        item.SetBitmap(self._engine.GetSkinImage('Targetsm'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardTarget, item)
        self._currentcard = c
        c.PopupMenu(menu)

    def OnCardHandToGrave(self, arg=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_GRAVE)
        self.MoveCard(self._hand, self._grave, card)
        card.SetCardState(POS_GRAVE)
        card.Reparent(self._gravelistctrl)
        self.RefreshGrave()
        self.RefreshHand()
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_PLAYER)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to his graveyard.', card.GetCardName()), CHAT_PLAYER)
    
    def OnCardHandToStack1(self, arg=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_STACK_1)
        self.MoveCard(self._hand, self._stack1, card)
        card.SetCardState(POS_STACK_1)
        card.Reparent(self._stack_1_listctrl)
        self.RefreshStack1()
        self.RefreshHand()
        self.WriteGameMessage(self._engine.GetLangString('sent %s to Stack 1.', card.GetCardName()), CHAT_PLAYER)
    
    def OnCardHandToStack2(self, arg=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_STACK_2)
        self.MoveCard(self._hand, self._stack2, card)
        card.SetCardState(POS_STACK_2)
        card.Reparent(self._stack_2_listctrl)
        self.RefreshStack2()
        self.RefreshHand()
        self.WriteGameMessage(self._engine.GetLangString('sent %s to Stack 2.', card.GetCardName()), CHAT_PLAYER)
    
    def OnCardHandToStack3(self, arg=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_STACK_3)
        self.MoveCard(self._hand, self._stack3, card)
        card.SetCardState(POS_STACK_3)
        card.Reparent(self._stack_3_listctrl)
        self.RefreshStack3()
        self.RefreshHand()
        self.WriteGameMessage(self._engine.GetLangString('sent %s to Stack 3.', card.GetCardName()), CHAT_PLAYER)
    
    def OnCardHandToStack4(self, arg=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_STACK_4)
        self.MoveCard(self._hand, self._stack4, card)
        card.SetCardState(POS_STACK_4)
        card.Reparent(self._stack_4_listctrl)
        self.RefreshStack4()
        self.RefreshHand()
        self.WriteGameMessage(self._engine.GetLangString('sent %s to Stack 4.', card.GetCardName()), CHAT_PLAYER)
    
    def OnCardHandToStack5(self, arg=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_STACK_5)
        self.MoveCard(self._hand, self._stack5, card)
        card.SetCardState(POS_STACK_5)
        card.Reparent(self._stack_5_listctrl)
        self.RefreshStack5()
        self.RefreshHand()
        self.WriteGameMessage(self._engine.GetLangString('sent %s to Stack 5.', card.GetCardName()), CHAT_PLAYER)

    def OnCardHandToRFG(self, arg=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_RFG)
        self.MoveCard(self._hand, self._rfg, card)
        card.SetCardState(POS_RFG)
        card.Reparent(self._rfglistctrl)
        self.RefreshRFG()
        self.RefreshHand()
        self.WriteGameMessage(self._engine.GetLangString('removed ') + card.GetCardName() + self._engine.GetLangString(' from game.'), CHAT_PLAYER)

    def OnCardHandToDeckShuffle(self, arg=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_DECK, 2) # Deck-Shuffle
        self.MoveCard(self._hand, self._deck, card)
        card.SetCardState(POS_DECK)
        card.Reparent(self._decklistctrl)
        self.WriteGameMessage(self._engine.GetLangString('sent ') + 'card' + self._engine.GetLangString(' to his deck.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)
        self.Shuffle()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        #self.RefreshDeck()
        self.RefreshHand()
 
    def OnCardShuffleHand(self, arg=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_HAND, 8) # Deck-Shuffle
        self.MoveCard(self._hand, self._hand, card)
        card.SetCardState(POS_HAND)
        self.ShuffleHand()
        self.RefreshHand()
        
    def OnCardHide(self, arg=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_HAND, 8) # Deck-Shuffle
        self.MoveCard(self._hand, self._hand, card)
        if card.IsFaceUp():
            card.SetCardState(POS_HAND, face=FACE_DOWN)
        else:
            card.SetCardState(POS_HAND, face=FACE_UP)
        self.ShuffleHand()
        self.RefreshHand()

    
    def OnCardHandToTopDeck(self, arg=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_DECK, 1) # Top-Deck
        self.MoveCardToTop(self._hand, self._deck, card)
        card.SetCardState(POS_DECK)
        card.Reparent(self._decklistctrl)
        self.RefreshDeck()
        self.RefreshHand()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the top of his deck.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)

    def OnCardHandToBottomDeck(self, arg=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_DECK, 0) # Bottom-Deck
        self.MoveCardToBottom(self._hand, self._deck, card)
        card.SetCardState(POS_DECK)
        card.Reparent(self._decklistctrl)
        self.RefreshDeck()
        self.RefreshHand()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the bottom of his deck.') + ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)
    
    def OnHandMTActivate(self, arg=None):
        card = self._currentcard[0]
        x = self._currentcard[1]
        y = self._currentcard[2]
        self.WriteMoveCardPacket(card, POS_OPP_FIELD, 0, x, y)
        card.SetCardState(POS_FIELD)
        self.MoveCard(self._hand, self._field, card)
        card.Reparent(self._fieldctrl)
        self.RefreshHand()
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('place ') + card.GetCardName() + self._engine.GetLangString(' on the field.'), CHAT_PLAYER)
    
    def OnHandMTPosition(self, arg=None):
        card = self._currentcard[0]
        x = self._currentcard[1]
        y = self._currentcard[2]
        self.WriteMoveCardPacket(card, POS_OPP_FIELD, 1, x, y)
        card.SetCardState(POS_FIELD, face=FACE_DOWN)
        self.MoveCard(self._hand, self._field, card)
        card.Reparent(self._fieldctrl)
        self.RefreshHand()
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('place a M/T on the field.'), CHAT_PLAYER)
    
    def OnHandMonsterSummon(self, arg=None):
        card = self._currentcard[0]
        x = self._currentcard[1]
        y = self._currentcard[2]
        self.WriteMoveCardPacket(card, POS_OPP_FIELD, 0, x, y)
        card.SetCardState(POS_FIELD)
        self.MoveCard(self._hand, self._field, card)
        card.Reparent(self._fieldctrl)
        self.RefreshHand()
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('place ') + card.GetCardName() + self._engine.GetLangString(' on the field.'), CHAT_PLAYER)
    
    def OnHandMonsterPosition(self, arg=None):
        card = self._currentcard[0]
        x = self._currentcard[1]
        y = self._currentcard[2]
        self.WriteMoveCardPacket(card, POS_OPP_FIELD, 2, x, y)
        card.SetCardState(POS_FIELD, CARD_HORIZONTAL, FACE_DOWN)
        self.MoveCard(self._hand, self._field, card)
        card.Reparent(self._fieldctrl)
        self.RefreshHand()
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('place a monster on the field.'), CHAT_PLAYER)

    def OnOpponentCardHandToGrave(self, arg=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponenthand, self._opponentgrave, card)
        card.SetCardState(POS_OPP_GRAVE)
        card.Reparent(self._opponentgravelistctrl)
        self.RefreshOpponentGrave()
        self.RefreshOpponentHand()
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_OPPONENT)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to his graveyard.', card.GetCardName()), CHAT_OPPONENT)

    def OnOpponentCardHandToRFG(self, arg=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponenthand, self._opponentrfg, card)
        card.SetCardState(POS_OPP_RFG)
        card.Reparent(self._opponentrfglistctrl)
        self.RefreshOpponentRFG()
        self.RefreshOpponentHand()
        self.WriteGameMessage(self._engine.GetLangString('removed ') + card.GetCardName() + self._engine.GetLangString(' from game.'), CHAT_OPPONENT)

    def OnOpponentCardHandToDeckShuffle(self, arg=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponenthand, self._opponentdeck, card)
        card.SetCardState(POS_OPP_DECK)
        card.Reparent(self._opponentdecklistctrl)
        self.RefreshOpponentDeck()
        self.RefreshOpponentHand()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + 'card' + self._engine.GetLangString(' to his deck.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)

    def OnOpponentCardHandToTopDeck(self, arg=None):
        card = self._opponentcurrentcard
        self.MoveCardToTop(self._opponenthand, self._opponentdeck, card)
        card.SetCardState(POS_OPP_DECK)
        card.Reparent(self._opponentdecklistctrl)
        self.RefreshOpponentDeck()
        self.RefreshOpponentHand()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the top of his deck.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)

    def OnOpponentCardHandToBottomDeck(self, arg=None):
        card = self._opponentcurrentcard
        self.MoveCardToBottom(self._opponenthand, self._opponentdeck, card)
        card.SetCardState(POS_OPP_DECK)
        card.Reparent(self._opponentdecklistctrl)
        self.RefreshOpponentDeck()
        self.RefreshOpponentHand()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the bottom of his deck.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)
    
    def OnOpponentHandMTActivate(self, arg=None):
        card = self._opponentcurrentcard[0]
        x = self._opponentcurrentcard[1]
        y = self._opponentcurrentcard[2]
        card.SetCardState(POS_OPP_FIELD)
        self.MoveCard(self._opponenthand, self._opponentfield, card)
        card.Reparent(self._opponentfieldctrl)
        self.RefreshOpponentHand()
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('place ') + card.GetCardName() + self._engine.GetLangString(' on the field.'), CHAT_OPPONENT)
    
    def OnOpponentHandMTPosition(self, arg=None):
        card = self._opponentcurrentcard[0]
        x = self._opponentcurrentcard[1]
        y = self._opponentcurrentcard[2]
        card.SetCardState(POS_OPP_FIELD, face=FACE_DOWN)
        self.MoveCard(self._opponenthand, self._opponentfield, card)
        card.Reparent(self._opponentfieldctrl)
        self.RefreshOpponentHand()
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('place a M/T on the field.'), CHAT_OPPONENT)
    
    def OnOpponentHandMonsterSummon(self, arg=None):
        card = self._opponentcurrentcard[0]
        x = self._opponentcurrentcard[1]
        y = self._opponentcurrentcard[2]
        card.SetCardState(POS_OPP_FIELD)
        self.MoveCard(self._opponenthand, self._opponentfield, card)
        card.Reparent(self._opponentfieldctrl)
        self.RefreshOpponentHand()
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('place ') + card.GetCardName() + self._engine.GetLangString(' on the field.'), CHAT_OPPONENT)
    
    def OnOpponentHandMonsterPosition(self, arg=None):
        card = self._opponentcurrentcard[0]
        x = self._opponentcurrentcard[1]
        y = self._opponentcurrentcard[2]
        card.SetCardState(POS_OPP_FIELD, CARD_HORIZONTAL, FACE_DOWN)
        self.MoveCard(self._opponenthand, self._opponentfield, card)
        card.Reparent(self._opponentfieldctrl)
        self.RefreshOpponentHand()
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('place a monster on the field.'), CHAT_OPPONENT)

    def OnCardFieldPopup(self, c):
        menu = wx.Menu()
        if c.IsMonster():
            if c.IsVertical():
                item = wx.MenuItem(menu, -1, self._engine.GetLangString('Attack'))
                item.SetBitmap(self._engine.GetSkinImage('Attack'))
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnCardFieldAttack, item)
                item = wx.MenuItem(menu, -1, self._engine.GetLangString('Flip/Horiz'))
                item.SetBitmap(self._engine.GetSkinImage('Flip'))
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnCardFieldFlipHorizontal, item)
            else:
                item = wx.MenuItem(menu, -1, self._engine.GetLangString('Flip/Vert'))
                item.SetBitmap(self._engine.GetSkinImage('Flip'))
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnCardFieldFlipVertical, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Grave'))
            item.SetBitmap(self._engine.GetSkinImage('Tograve'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldToGrave, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Hand'))
            item.SetBitmap(self._engine.GetSkinImage('Tohand'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldToHand, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To RFG'))
            item.SetBitmap(self._engine.GetSkinImage('Torfg'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldToRFG, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Extra Deck'))
            item.SetBitmap(self._engine.GetSkinImage('Toextra'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldToFusionDeck, item)
            if c.IsVertical():
                item = wx.MenuItem(menu, -1, self._engine.GetLangString('Horizontal'))
                item.SetBitmap(self._engine.GetSkinImage('Horiz'))
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnCardFieldHorizontal, item)
            else:
                item = wx.MenuItem(menu, -1, self._engine.GetLangString('Vertical'))
                item.SetBitmap(self._engine.GetSkinImage('Vert'))
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnCardFieldVertical, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('Flip'))
            item.SetBitmap(self._engine.GetSkinImage('Setst'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldFlip, item)
        else:
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('Activate'))
            item.SetBitmap(self._engine.GetSkinImage('Activate'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldFlip, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Grave'))
            item.SetBitmap(self._engine.GetSkinImage('Tograve'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldToGrave, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Hand'))
            item.SetBitmap(self._engine.GetSkinImage('Tohand'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldToHand, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To RFG'))
            item.SetBitmap(self._engine.GetSkinImage('Torfg'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldToRFG, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Extra Deck'))
            item.SetBitmap(self._engine.GetSkinImage('Toextra'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldToFusionDeck, item)
            if c.IsVertical():
                item = wx.MenuItem(menu, -1, self._engine.GetLangString('Horizontal'))
                item.SetBitmap(self._engine.GetSkinImage('Horiz'))
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnCardFieldHorizontal, item)
            else:
                item = wx.MenuItem(menu, -1, self._engine.GetLangString('Vertical'))
                item.SetBitmap(self._engine.GetSkinImage('Vert'))
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.OnCardFieldVertical, item)
        if not c.IsFusion():
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Top-Deck'))
            item.SetBitmap(self._engine.GetSkinImage('Totopdeck'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldToTopDeck, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Bottom-Deck'))
            item.SetBitmap(self._engine.GetSkinImage('Tobottomdeck'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldToBottomDeck, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Deck-Shuffle'))
            item.SetBitmap(self._engine.GetSkinImage('Todecksh'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldToDeckShuffle, item)
        else:
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Extra-Deck'))
            item.SetBitmap(self._engine.GetSkinImage('Toextra'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardFieldToFusionDeck, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('Target'))
        item.SetBitmap(self._engine.GetSkinImage('Targetsm'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardTarget, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('Add Counter'))
        item.SetBitmap(self._engine.GetSkinImage('CounterA'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardAddCounter, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('Remove Counter'))
        item.SetBitmap(self._engine.GetSkinImage('Counterm'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardRemoveCounter, item)
       # Not working.
       # item = wx.MenuItem(menu, -1, self._engine.GetLangString('Change Control'))
       # item.SetBitmap(self._engine.GetSkinImage('Counterm'))
       # menu.AppendItem(item)
       # self.Bind(wx.EVT_MENU, self.OnCardChangeControl, item)
        self._currentcard = c
        self.PopupMenu(menu)

    def OnCardFieldAttack(self, event=None):
        card = self._currentcard
        self.WriteChatPacket(self._engine.GetLangString('Attack with ') + card.GetCardName())
        self.WriteChatMessage(self._engine.GetLangString('Attack with ')+card.GetCardName(), CHAT_PLAYER)

    def OnCardFieldFlip(self, event=None):
        card = self._currentcard
        self.WriteFlipCardPacket(card, 0)
        if card.IsFaceUp():
            card.FaceDown()
            self.WriteGameMessage(self._engine.GetLangString('flipped ') + card.GetCardName() + self._engine.GetLangString(' face down.'), CHAT_PLAYER)
        else:
            card.FaceUp()
            self.WriteGameMessage(self._engine.GetLangString('flipped ') + card.GetCardName() + self._engine.GetLangString(' face up.'), CHAT_PLAYER)
        card.RefreshTexture()
        card.SetPosition(self.PositionCard(card, card.GetPositionTuple()[0], card.GetPositionTuple()[1]))
        card.Hide()
        card.Show()
    
    def OnCardFieldActivate(self, event=None):
        card = self._currentcard
        self.WriteFlipCardPacket(card, 0)
        if card.IsFaceUp():
            card.FaceDown()
            self.WriteGameMessage(self._engine.GetLangString('flipped ') + card.GetCardName() + self._engine.GetLangString(' face down.'), CHAT_PLAYER)
        else:
            card.FaceUp()
            self.WriteGameMessage(self._engine.GetLangString('activated ') + card.GetCardName() + self._engine.GetLangString(' .'), CHAT_PLAYER)
        card.RefreshTexture()
        card.SetPosition(self.PositionCard(card, card.GetPositionTuple()[0], card.GetPositionTuple()[1]))
        card.Hide()
        card.Show()

    def OnCardFieldFlipHorizontal(self, event=None):
        card = self._currentcard
        self.WriteFlipCardPacket(card, 1)
        card.FaceDown()
        card.Horizontal()
        card.RefreshTexture()
        card.SetPosition(self.PositionCard(card, card.GetPositionTuple()[0], card.GetPositionTuple()[1]))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('flipped ') + card.GetCardName() + self._engine.GetLangString(' face-down horizontal.'), CHAT_PLAYER)

    def OnCardFieldFlipVertical(self, event=None):
        card = self._currentcard
        self.WriteFlipCardPacket(card, 2)
        card.FaceUp()
        card.Vertical()
        card.RefreshTexture()
        card.SetPosition(self.PositionCard(card, card.GetPositionTuple()[0], card.GetPositionTuple()[1]))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('flipped ') + card.GetCardName() + self._engine.GetLangString(' face-up vertical.'), CHAT_PLAYER)

    def OnCardFieldHorizontal(self, event=None):
        card = self._currentcard
        self.WriteFlipCardPacket(card, 3)
        card.Horizontal()
        card.RefreshTexture()
        card.SetPosition(self.PositionCard(card, card.GetPositionTuple()[0], card.GetPositionTuple()[1]))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('turned ') + card.GetCardName() + self._engine.GetLangString(' horizontal.'), CHAT_PLAYER)

    def OnCardFieldVertical(self, event=None):
        card = self._currentcard
        self.WriteFlipCardPacket(card, 4)
        card.Vertical()
        card.RefreshTexture()
        card.SetPosition(self.PositionCard(card, card.GetPositionTuple()[0], card.GetPositionTuple()[1]))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('turned ') + card.GetCardName() + self._engine.GetLangString(' vertical.'), CHAT_PLAYER)

    def OnCardFieldToGrave(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_GRAVE)
        self.MoveCard(self._field, self._grave, card)
        card.SetCardState(POS_GRAVE)
        card.Reparent(self._gravelistctrl)
        self.RefreshGrave()
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_PLAYER)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to his graveyard.', card.GetCardName()), CHAT_PLAYER)
    
    def OnCardFieldToStack1(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_STACK_1)
        self.MoveCard(self._field, self._stack1, card)
        card.SetCardState(POS_STACK_1)
        card.Reparent(self._stack_1_listctrl)
        self.RefreshStack1()
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_PLAYER)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to Stack 1.', card.GetCardName()), CHAT_PLAYER)
        
    def OnCardFieldToStack2(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_STACK_2)
        self.MoveCard(self._field, self._stack2, card)
        card.SetCardState(POS_STACK_2)
        card.Reparent(self._stack_2_listctrl)
        self.RefreshStack2()
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_PLAYER)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to Stack 2.', card.GetCardName()), CHAT_PLAYER)
        
    def OnCardFieldToStack3(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_STACK_3)
        self.MoveCard(self._field, self._stack3, card)
        card.SetCardState(POS_STACK_3)
        card.Reparent(self._stack_3_listctrl)
        self.RefreshStack3()
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_PLAYER)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to Stack 3.', card.GetCardName()), CHAT_PLAYER)
        
    def OnCardFieldToStack4(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_STACK_4)
        self.MoveCard(self._field, self._stack4, card)
        card.SetCardState(POS_STACK_4)
        card.Reparent(self._stack_4_listctrl)
        self.RefreshStack4()
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_PLAYER)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to Stack 4.', card.GetCardName()), CHAT_PLAYER)
        
    def OnCardFieldToStack5(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_STACK_5)
        self.MoveCard(self._field, self._stack5, card)
        card.SetCardState(POS_STACK_5)
        card.Reparent(self._stack_5_listctrl)
        self.RefreshStack5()
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_PLAYER)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to Stack 5.', card.GetCardName()), CHAT_PLAYER)
    
    def OnCardFieldToRFG(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_RFG)
        self.MoveCard(self._field, self._rfg, card)
        card.SetCardState(POS_RFG)
        card.Reparent(self._rfglistctrl)
        self.RefreshRFG()
        self.WriteGameMessage(self._engine.GetLangString('removed ') + card.GetCardName() + self._engine.GetLangString(' from game.'), CHAT_PLAYER)

    def OnCardFieldToFusionDeck(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_FUSIONDECK)
        self.MoveCard(self._field, self._fusiondeck, card)
        card.SetCardState(POS_FUSIONDECK)
        card.Reparent(self._fusiondecklistctrl)
        self.RefreshFusionDeck()
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his Extra Deck.'), CHAT_PLAYER)

    def OnCardFieldToTopDeck(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_DECK, 1)
        if card.IsFaceUp():
            self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the top of his deck.')+ ' ' + str(len(self._deck)+1) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)
        else:
            self.WriteGameMessage(self._engine.GetLangString('sent a card to the top of his deck.')+ ' ' + str(len(self._deck)+1) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)
        self.MoveCardToTop(self._field, self._deck, card)
        card.SetCardState(POS_DECK)
        card.Reparent(self._decklistctrl)
        self.RefreshDeck()
        self._deckcounttext.SetLabel(str(len(self._deck)))

    def OnCardFieldToBottomDeck(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_DECK, 0)
        if card.IsFaceUp():
            self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the bottom of his deck.')+ ' ' + str(len(self._deck)+1) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)
        else:
            self.WriteGameMessage(self._engine.GetLangString('sent a card to the bottom of his deck.')+ ' ' + str(len(self._deck)+1) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)
        self.MoveCardToBottom(self._field, self._deck, card)
        card.SetCardState(POS_DECK)
        card.Reparent(self._decklistctrl)
        self.RefreshDeck()
        self._deckcounttext.SetLabel(str(len(self._deck)))

    def OnCardFieldToDeckShuffle(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_DECK, 2)
        if card.IsFaceUp():
            self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his deck.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)
        else:
            self.WriteGameMessage(self._engine.GetLangString('sent a card to his deck.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)
        self.MoveCard(self._field, self._deck, card)
        card.SetCardState(POS_DECK)
        card.Reparent(self._decklistctrl)
        self.Shuffle()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        #self.RefreshDeck()

    def OnCardFieldToHand(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_HAND)
        if card.IsFaceUp():
            self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his hand.'), CHAT_PLAYER)
        else:
            self.WriteGameMessage(self._engine.GetLangString('sent a card to his hand.'), CHAT_PLAYER)
        self.MoveCardToBottom(self._field, self._hand, card)
        card.SetCardState(POS_HAND)
        card.Reparent(self._handctrl)
        self.RefreshHand()

    # Opponent Field
    def OnOpponentCardFieldFlip(self, event=None):
        card = self._opponentcurrentcard
        if card.IsFaceUp():
            card.FaceDown()
            self.WriteGameMessage(self._engine.GetLangString('flipped ') + card.GetCardName() + self._engine.GetLangString(' face down.'), CHAT_OPPONENT)
        else:
            card.FaceUp()
            self.WriteGameMessage(self._engine.GetLangString('flipped ') + card.GetCardName() + self._engine.GetLangString(' face up.'), CHAT_OPPONENT)
        card.RefreshTexture()
        card.SetPosition(self.PositionCard(card, card.GetPositionTuple()[0], card.GetPositionTuple()[1]))
        card.Hide()
        card.Show()

    def OnOpponentCardFieldFlipHorizontal(self, event=None):
        card = self._opponentcurrentcard
        card.FaceDown()
        card.Horizontal()
        card.RefreshTexture()
        card.SetPosition(self.PositionCard(card, card.GetPositionTuple()[0], card.GetPositionTuple()[1]))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('flipped ') + card.GetCardName() + self._engine.GetLangString(' face-down horizontal.'), CHAT_OPPONENT)

    def OnOpponentCardFieldFlipVertical(self, event=None):
        card = self._opponentcurrentcard
        card.FaceUp()
        card.Vertical()
        card.RefreshTexture()
        card.SetPosition(self.PositionCard(card, card.GetPositionTuple()[0], card.GetPositionTuple()[1]))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('flipped ') + card.GetCardName() + self._engine.GetLangString(' face-up vertical.'), CHAT_OPPONENT)

    def OnOpponentCardFieldHorizontal(self, event=None):
        card = self._opponentcurrentcard
        card.Horizontal()
        card.RefreshTexture()
        card.SetPosition(self.PositionCard(card, card.GetPositionTuple()[0], card.GetPositionTuple()[1]))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('turned ') + card.GetCardName() + self._engine.GetLangString(' horizontal.'), CHAT_OPPONENT)

    def OnOpponentCardFieldVertical(self, event=None):
        card = self._opponentcurrentcard
        card.Vertical()
        card.RefreshTexture()
        card.SetPosition(self.PositionCard(card, card.GetPositionTuple()[0], card.GetPositionTuple()[1]))
        card.Hide()
        card.Show()
        self.WriteGameMessage(self._engine.GetLangString('turned ') + card.GetCardName() + self._engine.GetLangString(' vertical.'), CHAT_OPPONENT)
    
    def OnOpponentCardFieldToFusionDeck(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentfield, self._opponentfusiondeck, card)
        card.SetCardState(POS_OPP_FUSIONDECK)
        card.Reparent(self._opponentfusiondecklistctrl)
        self.RefreshOpponentFusionDeck()
        self.WriteGameMessage(self._engine.GetLangString('sent %s to his Extra Deck.', card.GetCardName()), CHAT_OPPONENT)
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_OPPONENT)
   
    def OnOpponentCardFieldToGrave(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentfield, self._opponentgrave, card)
        card.SetCardState(POS_OPP_GRAVE)
        card.Reparent(self._opponentgravelistctrl)
        self.RefreshOpponentGrave()
        self.WriteGameMessage(self._engine.GetLangString('sent %s to his Graveyard.', card.GetCardName()), CHAT_OPPONENT)
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_OPPONENT)

    def OnOpponentCardFieldToRFG(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentfield, self._opponentrfg, card)
        card.SetCardState(POS_OPP_RFG)
        card.Reparent(self._opponentrfglistctrl)
        self.RefreshOpponentRFG()
        self.WriteGameMessage(self._engine.GetLangString('removed ') + card.GetCardName() + self._engine.GetLangString(' from game.'), CHAT_OPPONENT)

    def OnOpponentCardFieldToTopDeck(self, event=None):
        card = self._opponentcurrentcard
        if card.IsFaceUp():
            self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the top of his deck.')+ ' ' + str(len(self._opponentdeck)+1) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)
        else:
            self.WriteGameMessage(self._engine.GetLangString('sent a card to the top of his deck.')+ ' ' + str(len(self._opponentdeck)+1) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)
        self.MoveCardToTop(self._opponentfield, self._opponentdeck, card)
        card.SetCardState(POS_OPP_DECK)
        card.Reparent(self._opponentdecklistctrl)
        self.RefreshOpponentDeck()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))

    def OnOpponentCardFieldToBottomDeck(self, event=None):
        card = self._opponentcurrentcard
        if card.IsFaceUp():
            self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the bottom of his deck.')+ ' ' + str(len(self._opponentdeck)+1) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)
        else:
            self.WriteGameMessage(self._engine.GetLangString('sent a card to the bottom of his deck.')+ ' ' + str(len(self._opponentdeck)+1) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)
        self.MoveCardToBottom(self._opponentfield, self._opponentdeck, card)
        card.SetCardState(POS_OPP_DECK)
        card.Reparent(self._opponentdecklistctrl)
        self.RefreshOpponentDeck()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))

    def OnOpponentCardFieldToDeckShuffle(self, event=None):
        card = self._opponentcurrentcard
        if card.IsFaceUp():
            self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his deck.')+ ' ' + str(len(self._opponentdeck)+1) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)
        else:
            self.WriteGameMessage(self._engine.GetLangString('sent a card to his deck.')+ ' ' + str(len(self._opponentdeck)+1) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)
        self.MoveCard(self._opponentfield, self._opponentdeck, card)
        card.SetCardState(POS_OPP_DECK)
        card.Reparent(self._opponentdecklistctrl)
        self.RefreshOpponentDeck()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))

    def OnOpponentCardFieldToHand(self, event=None):
        card = self._opponentcurrentcard
        if card.IsFaceUp():
            self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his hand.'), CHAT_OPPONENT)
        else:
            self.WriteGameMessage(self._engine.GetLangString('sent a card to his hand.'), CHAT_OPPONENT)
        self.MoveCardToBottom(self._opponentfield, self._opponenthand, card)
        card.SetCardState(POS_OPP_HAND, face=FACE_DOWN)
        card.Reparent(self._opponenthandctrl)
        self.RefreshOpponentHand()

    #Grave
    def OnCardGravePopup(self, c):
        menu = wx.Menu()
        if not c.IsFusion():
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Hand'))
            item.SetBitmap(self._engine.GetSkinImage('Tohand'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardGraveToHand, item)
        else:
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Extra-Deck'))
            item.SetBitmap(self._engine.GetSkinImage('Toextra'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardGraveToFusionDeck, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('To RFG'))
        item.SetBitmap(self._engine.GetSkinImage('Torfg'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardGraveToRFG, item)
        if not c.IsFusion():
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Deck/Shuffle'))
            item.SetBitmap(self._engine.GetSkinImage('Todecksh'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardGraveToDeckShuffle, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Top-Deck'))
            item.SetBitmap(self._engine.GetSkinImage('Totopdeck'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardGraveToTopDeck, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Bottom-Deck'))
            item.SetBitmap(self._engine.GetSkinImage('Tobottomdeck'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardGraveToBottomDeck, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('Target'))
        item.SetBitmap(self._engine.GetSkinImage('Targetsm'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardTarget, item)
        self._currentcard = c
        c.PopupMenu(menu)
        
    def OnCardGraveToHand(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_HAND)
        self.MoveCardToBottom(self._grave, self._hand, card)
        card.SetCardState(POS_HAND)
        card.Reparent(self._handctrl)
        self.RefreshHand()
        self.RefreshGrave()
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his hand.'), CHAT_PLAYER)
    
    def OnCardStack_1_ToHand(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_HAND)
        self.MoveCardToBottom(self._stack1, self._hand, card)
        card.SetCardState(POS_HAND)
        card.Reparent(self._handctrl)
        self.RefreshHand()
        self.RefreshStack1()
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his hand.'), CHAT_PLAYER)
    
    def OnCardStack_2_ToHand(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_HAND)
        self.MoveCardToBottom(self._stack2, self._hand, card)
        card.SetCardState(POS_HAND)
        card.Reparent(self._handctrl)
        self.RefreshHand()
        self.RefreshStack2()
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his hand.'), CHAT_PLAYER)
   
    def OnCardStack_3_ToHand(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_HAND)
        self.MoveCardToBottom(self._stack3, self._hand, card)
        card.SetCardState(POS_HAND)
        card.Reparent(self._handctrl)
        self.RefreshHand()
        self.RefreshStack3()
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his hand.'), CHAT_PLAYER)
    
    def OnCardStack_4_ToHand(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_HAND)
        self.MoveCardToBottom(self._stack4, self._hand, card)
        card.SetCardState(POS_HAND)
        card.Reparent(self._handctrl)
        self.RefreshHand()
        self.RefreshStack4()
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his hand.'), CHAT_PLAYER)
    
    def OnCardStack_5_ToHand(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_HAND)
        self.MoveCardToBottom(self._stack5, self._hand, card)
        card.SetCardState(POS_HAND)
        card.Reparent(self._handctrl)
        self.RefreshHand()
        self.RefreshStack5()
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his hand.'), CHAT_PLAYER)

    def OnCardGraveToFusionDeck(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_FUSIONDECK)
        self.MoveCard(self._grave, self._fusiondeck, card)
        card.SetCardState(POS_FUSIONDECK)
        card.Reparent(self._fusiondecklistctrl)
        self.RefreshGrave()
        self.RefreshFusionDeck()
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his Extra Deck.'), CHAT_PLAYER)

    def OnCardGraveToTopDeck(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_DECK, 1)
        self.MoveCardToTop(self._grave, self._deck, card)
        card.SetCardState(POS_DECK)
        card.Reparent(self._decklistctrl)
        self.RefreshDeck()
        self.RefreshGrave()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the top of his deck.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)

    def OnCardGraveToBottomDeck(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_DECK, 0)
        self.MoveCardToBottom(self._grave, self._deck, card)
        card.SetCardState(POS_DECK)
        card.Reparent(self._decklistctrl)
        self.RefreshDeck()
        self.RefreshGrave()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the bottom of his deck.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)

    def OnCardGraveToDeckShuffle(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_DECK, 2)
        self.MoveCard(self._grave, self._deck, card)
        card.SetCardState(POS_DECK)
        card.Reparent(self._decklistctrl)
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his deck.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)
        self.Shuffle()
        #self.RefreshDeck()
        self.RefreshGrave()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        

    def OnCardGraveToRFG(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_RFG)
        self.MoveCard(self._grave, self._rfg, card)
        card.SetCardState(POS_RFG)
        card.Reparent(self._rfglistctrl)
        self.RefreshRFG()
        self.RefreshGrave()
        self.WriteGameMessage(self._engine.GetLangString('removed ') + card.GetCardName() + self._engine.GetLangString(' from game.'), CHAT_PLAYER)

    def OnCardGraveToField(self, event=None):
        card = self._currentcard[0]
        x = self._currentcard[1]
        y = self._currentcard[2]
        self.WriteMoveCardPacket(card, POS_OPP_FIELD, 0, x, y)
        self.MoveCard(self._grave, self._field, card)
        card.SetCardState(POS_FIELD)
        card.Reparent(self._fieldctrl)
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.RefreshGrave()
        self.WriteGameMessage(self._engine.GetLangString('place ') + card.GetCardName() + self._engine.GetLangString(' on the field.'), CHAT_PLAYER)

    #Opponent Grave
    def OnOpponentCardGraveToHand(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCardToBottom(self._opponentgrave, self._opponenthand, card)
        card.SetCardState(POS_OPP_HAND, face=FACE_DOWN)
        card.Reparent(self._opponenthandctrl)
        self.RefreshOpponentHand()
        self.RefreshOpponentGrave()
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his hand.'), CHAT_OPPONENT)

    def OnOpponentCardGraveToTopDeck(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCardToTop(self._opponentgrave, self._opponentdeck, card)
        card.SetCardState(POS_OPP_DECK)
        card.Reparent(self._opponentdecklistctrl)
        self.RefreshOpponentDeck()
        self.RefreshOpponentGrave()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the top of his deck.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)

    def OnOpponentCardGraveToBottomDeck(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCardToBottom(self._opponentgrave, self._opponentdeck, card)
        card.SetCardState(POS_OPP_DECK)
        card.Reparent(self._opponentdecklistctrl)
        self.RefreshOpponentDeck()
        self.RefreshopponentGrave()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the bottom of his deck.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)

    def OnOpponentCardGraveToDeckShuffle(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentgrave, self._opponentdeck, card)
        card.SetCardState(POS_OPP_DECK)
        card.Reparent(self._opponentdecklistctrl)
        self.RefreshOpponentDeck()
        self.RefreshOpponentGrave()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his deck.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)


    def OnOpponentCardGraveToRFG(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentgrave, self._opponentrfg, card)
        card.SetCardState(POS_OPP_RFG)
        card.Reparent(self._opponentrfglistctrl)
        self.RefreshOpponentRFG()
        self.RefreshOpponentGrave()
        self.WriteGameMessage(self._engine.GetLangString('removed ') + card.GetCardName() + self._engine.GetLangString(' from game.'), CHAT_OPPONENT)
    
    def OnOpponentCardGraveToFusionDeck(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentgrave, self._opponentfusiondeck, card)
        card.SetCardState(POS_OPP_FUSIONDECK)
        card.Reparent(self._opponentfusiondecklistctrl)
        self.RefreshOpponentFusionDeck()
        self.RefreshOpponentGrave()
        self.WriteGameMessage(self._engine.GetLangString('Send ') + card.GetCardName() + self._engine.GetLangString(' to his Extra deck.'), CHAT_OPPONENT)

    def OnOpponentCardGraveToField(self, event=None):
        card = self._opponentcurrentcard[0]
        x = self._opponentcurrentcard[1]
        y = self._opponentcurrentcard[2]
        self.MoveCard(self._opponentgrave, self._opponentfield, card)
        card.SetCardState(POS_OPP_FIELD)
        card.Reparent(self._opponentfieldctrl)
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.RefreshOpponentGrave()
        self.WriteGameMessage(self._engine.GetLangString('place ') + card.GetCardName() + self._engine.GetLangString(' on the field.'), CHAT_OPPONENT)

    #RFG
    def OnCardRFGPopup(self, c):
        menu = wx.Menu()
        if not c.IsFusion():
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Hand'))
            item.SetBitmap(self._engine.GetSkinImage('Tohand'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardRFGToHand, item)
        else:
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Extra-Deck'))
            item.SetBitmap(self._engine.GetSkinImage('Toextra'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardRFGToFusionDeck, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Grave'))
        item.SetBitmap(self._engine.GetSkinImage('Tograve'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardRFGToGrave, item)
        if not c.IsFusion():
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Deck/Shuffle'))
            item.SetBitmap(self._engine.GetSkinImage('Todecksh'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardRFGToDeckShuffle, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Top-Deck'))
            item.SetBitmap(self._engine.GetSkinImage('Totopdeck'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardRFGToTopDeck, item)
            item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Bottom-Deck'))
            item.SetBitmap(self._engine.GetSkinImage('Tobottomdeck'))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnCardRFGToBottomDeck, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('Target'))
        item.SetBitmap(self._engine.GetSkinImage('Targetsm'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardTarget, item)
        self._currentcard = c
        c.PopupMenu(menu)

    def OnCardRFGToHand(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_HAND)
        self.MoveCardToBottom(self._rfg, self._hand, card)
        card.SetCardState(POS_HAND)
        card.Reparent(self._handctrl)
        self.RefreshHand()
        self.RefreshRFG()
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his hand.'), CHAT_PLAYER)

    def OnCardRFGToFusionDeck(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_FUSIONDECK)
        self.MoveCard(self._rfg, self._fusiondeck, card)
        card.SetCardState(POS_FUSIONDECK)
        card.Reparent(self._fusiondecklistctrl)
        self.RefreshRFG()
        self.RefreshFusionDeck()
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his Extra Deck.'), CHAT_PLAYER)
    
    def OnCardDeckToSideDeck(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_SIDEDECK)
        self.MoveCard(self._deck, self._sidedeck, card)
        card.SetCardState(POS_SIDEDECK)
        card.Reparent(self._sidedecklistctrl)
        self.RefreshDeck()
        self.RefreshSideDeck()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        self.WriteGameMessage('moved card from Deck to Side Deck', CHAT_PLAYER)

    def OnCardRFGToTopDeck(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_DECK, 1)
        self.MoveCardToTop(self._rfg, self._deck, card)
        card.SetCardState(POS_DECK)
        card.Reparent(self._decklistctrl)
        self.RefreshDeck()
        self.RefreshRFG()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the top of his deck.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)

    def OnCardRFGToBottomDeck(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_DECK, 0)
        self.MoveCardToBottom(self._rfg, self._deck, card)
        card.SetCardState(POS_DECK)
        card.Reparent(self._decklistctrl)
        self.RefreshDeck()
        self.RefreshRFG()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the bottom of his deck.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)

    def OnCardRFGToDeckShuffle(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_DECK, 2)
        self.MoveCard(self._rfg, self._deck, card)
        card.SetCardState(POS_DECK)
        card.Reparent(self._decklistctrl)
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his deck.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)
        self.Shuffle()
        #self.RefreshDeck()
        self.RefreshRFG()
        self._deckcounttext.SetLabel(str(len(self._deck)))

    def OnCardRFGToGrave(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_GRAVE)
        self.MoveCard(self._rfg, self._grave, card)
        card.SetCardState(POS_GRAVE)
        card.Reparent(self._gravelistctrl)
        self.RefreshGrave()
        self.RefreshRFG()
        self.WriteGameMessage(self._engine.GetLangString('sent %s to his graveyard.', card.GetCardName()), CHAT_PLAYER)
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_PLAYER)

    def OnCardRFGToField(self, event=None):
        card = self._currentcard[0]
        x = self._currentcard[1]
        y = self._currentcard[2]
        self.WriteMoveCardPacket(card, POS_OPP_FIELD, 0, x, y)
        self.MoveCard(self._rfg, self._field, card)
        card.SetCardState(POS_FIELD)
        card.Reparent(self._fieldctrl)
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.RefreshRFG()
        self.WriteGameMessage(self._engine.GetLangString('place ') + card.GetCardName() + self._engine.GetLangString(' on the field.'), CHAT_PLAYER)

    # Opponent RFG
    def OnOpponentCardRFGToHand(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCardToBottom(self._opponentrfg, self._opponenthand, card)
        card.SetCardState(POS_OPP_HAND, face=FACE_DOWN)
        card.Reparent(self._opponenthandctrl)
        self.RefreshOpponentHand()
        self.RefreshOpponentRFG()
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his hand.'), CHAT_OPPONENT)

    def OnOpponentCardRFGToTopDeck(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCardToTop(self._opponentrfg, self._opponentdeck, card)
        card.SetCardState(POS_OPP_DECK)
        card.Reparent(self._opponentdecklistctrl)
        self.RefreshOpponentDeck()
        self.RefreshOpponentRFG()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the top of his deck.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)

    def OnOpponentCardRFGToBottomDeck(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCardToBottom(self._opponentrfg, self._opponentdeck, card)
        card.SetCardState(POS_OPP_DECK)
        card.Reparent(self._opponentdecklistctrl)
        self.RefreshOpponentDeck()
        self.RefreshOpponentRFG()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to the bottom of his deck.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)

    def OnOpponentCardRFGToDeckShuffle(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentrfg, self._opponentdeck, card)
        card.SetCardState(POS_OPP_DECK)
        card.Reparent(self._opponentdecklistctrl)
        self.RefreshOpponentDeck()
        self.RefreshOpponentRFG()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his deck.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)

    def OnOpponentCardRFGToFusionDeck(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentrfg, self._opponentfusiondeck, card)
        card.SetCardState(POS_OPP_FUSIONDECK)
        card.Reparent(self._opponentfusiondecklistctrl)
        self.RefreshOpponentFusionDeck()
        self.RefreshOpponentRFG()
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_OPPONENT)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to his Extra Deck.', card.GetCardName()), CHAT_OPPONENT)
    
    def OnOpponentCardDeckToSideDeck(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentdeck, self._opponentsidedeck, card)
        card.SetCardState(POS_OPP_SIDEDECK)
        card.Reparent(self._opponentsidedecklistctrl)
        self.RefreshOpponentSideDeck()
        self.RefreshOpponentDeck()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_OPPONENT)
        self.WriteGameMessage('moved card from Deck to Side Deck', CHAT_OPPONENT)
    
    def OnOpponentCardRFGToGrave(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentrfg, self._opponentgrave, card)
        card.SetCardState(POS_OPP_GRAVE)
        card.Reparent(self._opponentgravelistctrl)
        self.RefreshOpponentGrave()
        self.RefreshOpponentRFG()
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_OPPONENT)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to his graveyard.', card.GetCardName()), CHAT_OPPONENT)

    def OnOpponentCardRFGToField(self, event=None):
        card = self._opponentcurrentcard[0]
        x = self._opponentcurrentcard[1]
        y = self._opponentcurrentcard[2]
        self.MoveCard(self._opponentrfg, self._opponentfield, card)
        card.SetCardState(POS_OPP_FIELD)
        card.Reparent(self._opponentfieldctrl)
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.RefreshOpponentRFG()
        self.WriteGameMessage(self._engine.GetLangString('place ') + card.GetCardName() + self._engine.GetLangString(' on the field.'), CHAT_OPPONENT)

    #Deck
    def OnCardDeckPopup(self, c):
        menu = wx.Menu()
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Hand'))
        item.SetBitmap(self._engine.GetSkinImage('Tohand'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardDeckToHand, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Grave'))
        item.SetBitmap(self._engine.GetSkinImage('Tograve'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardDeckToGrave, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('To RFG'))
        item.SetBitmap(self._engine.GetSkinImage('Torfg'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardDeckToRFG, item)
        self._currentcard = c
        c.PopupMenu(menu)
    
    def OnCardSideDeckPopup(self, c):
        menu = wx.Menu()
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('To Deck'))
        item.SetBitmap(self._engine.GetSkinImage('Tohand'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnCardSideDeckToDeck, item)
        self._currentcard = c
        c.PopupMenu(menu)
        
    def OnCardDeckToHand(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_HAND)
        self.MoveCardToBottom(self._deck, self._hand, card)
        card.SetCardState(POS_HAND)
        card.Reparent(self._handctrl)
        self.RefreshHand()
        self.RefreshDeck()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his hand.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)

    def OnCardDeckToGrave(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_GRAVE)
        self.MoveCard(self._deck, self._grave, card)
        card.SetCardState(POS_GRAVE)
        card.Reparent(self._gravelistctrl)
        self.RefreshGrave()
        self.RefreshDeck()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_PLAYER)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to his graveyard.', card.GetCardName())+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)

    def OnCardDeckToRFG(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_RFG)
        self.MoveCard(self._deck, self._rfg, card)
        card.SetCardState(POS_RFG)
        card.Reparent(self._rfglistctrl)
        self.RefreshRFG()
        self.RefreshDeck()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        self.WriteGameMessage(self._engine.GetLangString('removed ') + card.GetCardName() + self._engine.GetLangString(' from game.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)

    def OnCardDeckToField(self, event=None):
        card = self._currentcard[0]
        x = self._currentcard[1]
        y = self._currentcard[2]
        self.WriteMoveCardPacket(card, POS_OPP_FIELD, 0, x, y)
        self.MoveCard(self._deck, self._field, card)
        card.SetCardState(POS_FIELD)
        card.Reparent(self._fieldctrl)
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.RefreshDeck()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        self.WriteGameMessage(self._engine.GetLangString('place ') + card.GetCardName() + self._engine.GetLangString(' on the field.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)
    #End

    #FusionDeck
    def OnCardFusionDeckToGrave(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_GRAVE)
        self.MoveCard(self._fusiondeck, self._grave, card)
        card.SetCardState(POS_GRAVE)
        card.Reparent(self._gravelistctrl)
        self.RefreshGrave()
        self.RefreshFusionDeck()
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_PLAYER)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to his graveyard.', card.GetCardName()), CHAT_PLAYER)
    
    def OnCardSideDeckToDeck(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_DECK)
        self.MoveCard(self._sidedeck, self._deck, card)
        card.SetCardState(POS_DECK)
        card.Reparent(self._decklistctrl)
        self.RefreshDeck()
        self.RefreshSideDeck()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_PLAYER)
        self.WriteGameMessage('moved card from Side Deck to Deck', CHAT_PLAYER)

    def OnCardFusionDeckToRFG(self, event=None):
        card = self._currentcard
        self.WriteMoveCardPacket(card, POS_OPP_RFG)
        self.MoveCard(self._fusiondeck, self._rfg, card)
        card.SetCardState(POS_RFG)
        card.Reparent(self._rfglistctrl)
        self.RefreshRFG()
        self.RefreshFusionDeck()
        self.WriteGameMessage(self._engine.GetLangString('removed ') + card.GetCardName() + self._engine.GetLangString(' from game.'), CHAT_PLAYER)

    def OnCardFusionDeckToField(self, event=None):
        card = self._currentcard[0]
        x = self._currentcard[1]
        y = self._currentcard[2]
        self.WriteMoveCardPacket(card, POS_OPP_FIELD, 0, x, y)
        self.MoveCard(self._fusiondeck, self._field, card)
        card.SetCardState(POS_FIELD)
        card.Reparent(self._fieldctrl)
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.RefreshFusionDeck()
        self.WriteGameMessage(self._engine.GetLangString('place ') + card.GetCardName() + self._engine.GetLangString(' on the field.'), CHAT_PLAYER)
    #End

    #Opponent Fusion
    def OnOpponentCardFusionDeckToField(self, event=None):
        card = self._opponentcurrentcard[0]
        x = self._opponentcurrentcard[1]
        y = self._opponentcurrentcard[2]
        self.MoveCard(self._opponentfusiondeck, self._opponentfield, card)
        card.SetCardState(POS_OPP_FIELD)
        card.Reparent(self._opponentfieldctrl)
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.RefreshOpponentFusionDeck()
        self.WriteGameMessage(self._engine.GetLangString('place ') + card.GetCardName() + self._engine.GetLangString(' on the field.'), CHAT_OPPONENT)

    def OnOpponentCardFusionDeckToGrave(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentfusiondeck, self._opponentgrave, card)
        card.SetCardState(POS_OPP_GRAVE)
        card.Reparent(self._opponentfieldctrl)
        self.RefreshOpponentFusionDeck()
        self.RefreshOpponentGrave()
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_OPPONENT)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to his graveyard.', card.GetCardName()), CHAT_OPPONENT)
        
    
    def OnOpponentCardSideDeckToDeck(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentsidedeck, self._opponentdeck, card)
        card.SetCardState(POS_OPP_DECK)
        card.Reparent(self._opponentdeckctrl)
        self.RefreshOpponentSideDeck()
        self.RefreshOpponentDeck()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_OPPONENT)
        self.WriteGameMessage('moved card from Side Deck to Deck', CHAT_OPPONENT)

    def OnOpponentCardFusionDeckToRFG(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentfusiondeck, self._opponentrfg, card)
        card.SetCardState(POS_OPP_RFG)
        card.Reparent(self._opponentfieldctrl)
        self.RefreshOpponentFusionDeck()
        self.RefreshOpponentRFG()
        self.WriteGameMessage(self._engine.GetLangString('removed ') + card.GetCardName() + self._engine.GetLangString('from game.'), CHAT_OPPONENT)

    
    # Opponent Deck
    def OnOpponentCardDeckToHand(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCardToBottom(self._opponentdeck, self._opponenthand, card)
        card.SetCardState(POS_OPP_HAND, face=FACE_DOWN)
        card.Reparent(self._opponenthandctrl)
        self.RefreshOpponentHand()
        self.RefreshOpponentDeck()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his hand.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)

    def OnOpponentCardDeckToGrave(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentdeck, self._opponentgrave, card)
        card.SetCardState(POS_OPP_GRAVE)
        card.Reparent(self._opponentgravelistctrl)
        self.RefreshOpponentGrave()
        self.RefreshOpponentDeck()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        #self.WriteGameMessage(self._engine.GetLangString('sent ') + card.GetCardName() + self._engine.GetLangString(' to his graveyard.'), CHAT_OPPONENT)
        self.WriteGameMessage(self._engine.GetLangString('sent %s to his graveyard.', card.GetCardName())+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)

    def OnOpponentCardDeckToRFG(self, event=None):
        card = self._opponentcurrentcard
        self.MoveCard(self._opponentdeck, self._opponentrfg, card)
        card.SetCardState(POS_OPP_RFG)
        card.Reparent(self._opponentrfglistctrl)
        self.RefreshOpponentRFG()
        self.RefreshOpponentDeck()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        self.WriteGameMessage(self._engine.GetLangString('removed ') + card.GetCardName() + self._engine.GetLangString(' from game.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)

    def OnOpponentCardDeckToField(self, event=None):
        card = self._opponentcurrentcard[0]
        x = self._opponentcurrentcard[1]
        y = self._opponentcurrentcard[2]
        self.MoveCard(self._opponentdeck, self._opponentfield, card)
        card.SetCardState(POS_OPP_FIELD)
        card.Reparent(self._opponentfieldctrl)
        card.SetPosition(self.PositionCard(card, x, y))
        card.Hide()
        card.Show()
        self.RefreshOpponentDeck()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        self.WriteGameMessage(self._engine.GetLangString('place ') + card.GetCardName() + self._engine.GetLangString(' on the field.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)
    #End

    def OnDeckDClick(self, event):
        self.OnDeckDraw()

    def OnDeckRClick(self, event):
        menu = wx.Menu()
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('Search Deck'))
        item.SetBitmap(self._engine.GetSkinImage('Searchdeck'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPopupDeckSearch, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('Shuffle'))
        item.SetBitmap(self._engine.GetSkinImage('Searchdeck'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPopupDeckShuffle, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('Draw and Reveal'))
        item.SetBitmap(self._engine.GetSkinImage('Drawsh'))
        
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPopupDeckDrawReveal, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('Discard Top Card'))
        item.SetBitmap(self._engine.GetSkinImage('Tograve'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPopupDeckDiscardTopCard, item)
        item = wx.MenuItem(menu, -1, self._engine.GetLangString('Reveal Top Card'))
        item.SetBitmap(self._engine.GetSkinImage('Vert'))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPopupDeckRevealTopCard, item)
        self.PopupMenu(menu)
    
    def OnPopupDeckDrawReveal(self, event):
        self.OnDeckDraw(1)
    
    def OnPopupDeckDiscardTopCard(self, event):
        card = self._deck[0]
        self.MoveCard(self._deck, self._grave, card)
        card.SetCardState(POS_GRAVE)
        card.Reparent(self._gravelistctrl)
        self.RefreshGrave()
        self.RefreshDeck()
        self._deckcounttext.SetLabel(str(len(self._deck)))
        self.WriteCardActionPacket(ACTION_DISCARDTOP)
        self.WriteGameMessage(self._engine.GetLangString('discarded ') + card.GetCardName() + self._engine.GetLangString(' from the top of his deck.')+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)
    
    def OnPopupDeckRevealTopCard(self, event):
        card = self._deck[0]
        self.WriteCardActionPacket(ACTION_REVEALTOP)
        self.WriteGameMessage(self._engine.GetLangString('revealed ') + card.GetCardName() + self._engine.GetLangString(' from the top of his deck.'), CHAT_PLAYER)

    def OnPopupDeckSearch(self, event=None):
        if self._decklistctrl.IsShown():
            self._decklistctrl.Hide()
            self.WriteLookPacket(LOOK_DECK_NO)
            self._deckctrl.SetTexture(self._engine.GetSkinImage('Deck'))
            self.WriteGameMessage(self._engine.GetLangString('end looking at his deck.'), CHAT_PLAYER)
        else:
            self._decklistctrl.Show()
            self.WriteLookPacket(LOOK_DECK_YES)
            self._deckctrl.SetTexture(self._engine.GetSkinImage('LookDeck'))
            self.WriteGameMessage(self._engine.GetLangString('is looking at his deck.'), CHAT_PLAYER)

    def OnPopupDeckShuffle(self, event):
        self.Shuffle()
    
    def OnOpponentActionDiscardTop(self, event = None):
        card = self._opponentdeck[0]
        self.MoveCard(self._opponentdeck, self._opponentgrave, card)
        card.SetCardState(POS_OPP_GRAVE)
        card.Reparent(self._opponentgravelistctrl)
        self.RefreshOpponentGrave()
        self.RefreshOpponentDeck()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        self.WriteGameMessage(self._engine.GetLangString('discarded ') + card.GetCardName() + self._engine.GetLangString(' from the top of his deck.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)
    
    def OnOpponentActionRevealTop(self, event=None):
        card = self._opponentdeck[0]
        self.WriteGameMessage(self._engine.GetLangString('revealed ') + card.GetCardName() + self._engine.GetLangString(' from the top of his deck.'), CHAT_OPPONENT)

    def OnGraveLClick(self, event=None):
        if self._gravelistctrl.IsShown():
            self._gravelistctrl.Hide()
            self.WriteLookPacket(LOOK_GRAVE_NO)
            self.WriteGameMessage(self._engine.GetLangString('end looking at his graveyard.'), CHAT_PLAYER)
        else:
            self._gravelistctrl.Show()
            self.WriteLookPacket(LOOK_GRAVE_YES)
            self.WriteGameMessage(self._engine.GetLangString('is looking at his graveyard.'), CHAT_PLAYER)
    
    def OnStack_1_LClick(self, event=None):
        if self._stack_1_listctrl.IsShown():
            self._stack_1_listctrl.Hide()
            self.WriteLookPacket(LOOK_STACK_1_NO)
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Stack 1.'), CHAT_PLAYER)
        else:
            self._stack_1_listctrl.Show()
            self.WriteLookPacket(LOOK_STACK_1_YES)
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Stack 1.'), CHAT_PLAYER)
    
    def OnStack_2_LClick(self, event=None):
        if self._stack_2_listctrl.IsShown():
            self._stack_2_listctrl.Hide()
            self.WriteLookPacket(LOOK_STACK_2_NO)
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Stack 2.'), CHAT_PLAYER)
        else:
            self._stack_2_listctrl.Show()
            self.WriteLookPacket(LOOK_STACK_2_YES)
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Stack 2.'), CHAT_PLAYER)
    
    def OnStack_3_LClick(self, event=None):
        if self._stack_3_listctrl.IsShown():
            self._stack_3_listctrl.Hide()
            self.WriteLookPacket(LOOK_STACK_3_NO)
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Stack 3.'), CHAT_PLAYER)
        else:
            self._stack_3_listctrl.Show()
            self.WriteLookPacket(LOOK_STACK_3_YES)
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Stack 3.'), CHAT_PLAYER)
    
    def OnStack_4_LClick(self, event=None):
        if self._stack_4_listctrl.IsShown():
            self._stack_4_listctrl.Hide()
            self.WriteLookPacket(LOOK_STACK_4_NO)
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Stack 4.'), CHAT_PLAYER)
        else:
            self._stack_4_listctrl.Show()
            self.WriteLookPacket(LOOK_STACK_4_YES)
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Stack 4.'), CHAT_PLAYER)
    
    def OnStack_5_LClick(self, event=None):
        if self._stack_5_listctrl.IsShown():
            self._stack_5_listctrl.Hide()
            self.WriteLookPacket(LOOK_STACK_5_NO)
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Stack 5.'), CHAT_PLAYER)
        else:
            self._stack_5_listctrl.Show()
            self.WriteLookPacket(LOOK_STACK_5_YES)
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Stack 5.'), CHAT_PLAYER)

    def OnOpponentGraveLClick(self, event=None):
        if self._opponentgravelistctrl.IsShown():
            self._opponentgravelistctrl.Hide()
            self.WriteLookPacket(LOOK_OPPONENT_GRAVE_NO)
            self.WriteGameMessage(self._engine.GetLangString("end looking at his opponent's graveyard."), CHAT_PLAYER)
        else:
            self._opponentgravelistctrl.Show()
            self.WriteLookPacket(LOOK_OPPONENT_GRAVE_YES)
            self.WriteGameMessage(self._engine.GetLangString("is looking at his opponent's graveyard."), CHAT_PLAYER)

    def OnNewNote(self, event):
        pos = self._fieldctrl.ScreenToClient(wx.GetMousePosition())
        Note(self._fieldctrl, (pos.x-25, pos.y-25), self)

    def OnDeckDraw(self, reveal=0):
        if len(self._deck) < 1:
            return
        c = self.RemoveCardFromTop(self._deck)
        c.SetCardState(POS_HAND)
        self.AddCardToBottom(self._hand, c)
        c.Reparent(self._handctrl)
        self.RefreshHand()
        self.RefreshDeck()
        self.WritePacket(packets.DrawPacket(reveal))
        self._deckcounttext.SetLabel(str(len(self._deck)))
        if reveal:
            self.WriteGameMessage(self._engine.GetLangString('drew ') + c.GetCardName() + '.'+ ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)
        else:
            self.WriteGameMessage(self._engine.GetLangString('drew a card.') + ' ' + str(len(self._deck)) +self._engine.GetLangString(' cards left.'), CHAT_PLAYER)

    def OnDeckDrawShow(self):
        self.OnDeckDraw(1)

    def OnOpponentDeckDraw(self, reveal=0):
        c = self.RemoveCardFromTop(self._opponentdeck)
        c.SetCardState(POS_OPP_HAND, face=FACE_DOWN)
        self.AddCardToBottom(self._opponenthand, c)
        c.Reparent(self._opponenthandctrl)
        self.RefreshOpponentHand()
        self.RefreshOpponentDeck()
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))
        if reveal:
            self.WriteGameMessage(self._engine.GetLangString('drew ') + c.GetCardName() + '.'+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)
        else:
            self.WriteGameMessage(self._engine.GetLangString('drew a card.')+ ' ' + str(len(self._opponentdeck)) +self._engine.GetLangString(' cards left.'), CHAT_OPPONENT)
    
    def OnCardFieldMove(self, c, x, y):
        c.SetPosition(self.PositionCard(c, x, y))
        self.WriteMoveCardPacket(c, POS_OPP_FIELD, 0, x, y)
        c.Hide()
        c.Show()
    
    def OnOpponentCardFieldMove(self, c, x, y):
        c.SetPosition(self.PositionCard(c, x, y))
        c.Hide()
        c.Show()

    def PositionCard(self, card, x, y):
        adj = True
        if self.Hit(x, y, wx.Rect(108,48,96,96)):
            x = 108
            y = 48
        elif self.Hit(x, y, wx.Rect(205,48,96,96)):
            x = 205
            y = 48
        elif self.Hit(x, y, wx.Rect(302,48,96,96)):
            x = 302
            y = 48
        elif self.Hit(x, y, wx.Rect(399,48,96,96)):
            x = 399
            y = 48
        elif self.Hit(x, y, wx.Rect(496,48,96,96)):
            x = 496
            y = 48
        elif self.Hit(x, y, wx.Rect(108,145,96,96)):
            x = 108
            y = 145
        elif self.Hit(x, y, wx.Rect(205,145,96,96)):
            x = 205
            y = 145
        elif self.Hit(x, y, wx.Rect(302,145,96,96)):
            x = 302
            y = 145
        elif self.Hit(x, y, wx.Rect(399,145,96,96)):
            x = 399
            y = 145
        elif self.Hit(x, y, wx.Rect(496,145,96,96)):
            x = 496
            y = 145
        elif self.Hit(x, y, wx.Rect(21,33,60,88)) and type(card) is CardControl:
            x = 21
            y = 33
            adj = False
        elif self.Hit(x, y, wx.Rect(618,168,60,88)) and type(card) is OpponentCardControl:
            x = 618
            y = 168
            adj = False
        else:
            x -= 30
            y -= 44
            adj = False 

        if adj:
            if card.IsHorizontal():
                x += 4
                y += 18
            else:
                x += 18
                y += 4
        return wx.Point(x,y)

    def OnCardDropOnField(self, x, y, data):
        c = self.GetCardFromSerial(data)
        self._currentcard = c
        if self.Hit(x, y, self._gravectrl.GetRect()):
            self.OnCardDropOnGrave(x, y, data)
        elif self.Hit(x, y, self._rfgctrl.GetRect()):
            self.OnCardDropOnRFG(x, y, data)
        elif self.Hit(x, y, self._stack1ctrl.GetRect()):
            self.OnCardDropOnStack1(x, y, data)
        elif self.Hit(x, y, self._stack2ctrl.GetRect()):
            self.OnCardDropOnStack2(x, y, data)
        elif self.Hit(x, y, self._stack3ctrl.GetRect()):
            self.OnCardDropOnStack3(x, y, data)
        elif self.Hit(x, y, self._stack4ctrl.GetRect()):
            self.OnCardDropOnStack4(x, y, data)
        elif self.Hit(x, y, self._stack5ctrl.GetRect()):
            self.OnCardDropOnStack5(x, y, data)
        elif self.Hit(x, y, wx.Rect(0,0,self._fieldctrl.GetSize().GetWidth(),self._fieldctrl.GetSize().GetHeight())):
            self._currentcard = (c,x,y)
            if c.GetCardPosition() == POS_FIELD:
                self.OnCardFieldMove(c, x, y)
            elif c.GetCardPosition() == POS_GRAVE:
                self.OnCardGraveToField()
            elif c.GetCardPosition() == POS_RFG:
                self.OnCardRFGToField()
            elif c.GetCardPosition() == POS_FUSIONDECK:
                self.OnCardFusionDeckToField()
            elif c.GetCardPosition() == POS_HAND:
                att = c.GetCardAttribute()
                if att == 'Trap' or att == 'Spell':
                    self.PopupMenu(self._hand_mt_menu)
                else:
                    self.PopupMenu(self._hand_monster_menu)
            elif c.GetCardPosition() == POS_DECK:
                self.OnCardDeckToField()
        self._consolectrl.SetFocus()

    def OnCardDropOnGrave(self, x, y, data):
        c = self.GetCardFromSerial(data)
        self._currentcard = c
        if c.GetCardPosition() == POS_HAND:
            self.OnCardHandToGrave()
        elif c.GetCardPosition() == POS_FIELD:
            self.OnCardFieldToGrave()
        elif c.GetCardPosition() == POS_DECK:
            self.OnCardDeckToGrave()
        elif c.GetCardPosition() == POS_RFG:
            self.OnCardRFGToGrave()
        elif c.GetCardPosition() == POS_FUSIONDECK:
            self.OnCardFusionDeckToGrave()
    
    def OnCardDropOnStack1(self, x, y, data):
        c = self.GetCardFromSerial(data)
        self._currentcard = c
        if c.GetCardPosition() == POS_HAND:
            self.OnCardHandToStack1()
        elif c.GetCardPosition() == POS_FIELD:
            self.OnCardFieldToStack1()
        elif c.GetCardPosition() == POS_DECK:
            self.OnCardDeckToStack1()
        elif c.GetCardPosition() == POS_RFG:
            self.OnCardRFGToStack1()
        elif c.GetCardPosition() == POS_FUSIONDECK:
            self.OnCardFusionDeckToStack1()
    
    def OnCardDropOnStack2(self, x, y, data):
        c = self.GetCardFromSerial(data)
        self._currentcard = c
        if c.GetCardPosition() == POS_HAND:
            self.OnCardHandToStack2()
        elif c.GetCardPosition() == POS_FIELD:
            self.OnCardFieldToStack2()
        elif c.GetCardPosition() == POS_DECK:
            self.OnCardDeckToStack2()
        elif c.GetCardPosition() == POS_RFG:
            self.OnCardRFGToStack2()
        elif c.GetCardPosition() == POS_FUSIONDECK:
            self.OnCardFusionDeckToStack2()
    
    def OnCardDropOnStack3(self, x, y, data):
        c = self.GetCardFromSerial(data)
        self._currentcard = c
        if c.GetCardPosition() == POS_HAND:
            self.OnCardHandToStack3()
        elif c.GetCardPosition() == POS_FIELD:
            self.OnCardFieldToStack3()
        elif c.GetCardPosition() == POS_DECK:
            self.OnCardDeckToStack3()
        elif c.GetCardPosition() == POS_RFG:
            self.OnCardRFGToStack3()
        elif c.GetCardPosition() == POS_FUSIONDECK:
            self.OnCardFusionDeckToStack3()
    
    def OnCardDropOnStack4(self, x, y, data):
        c = self.GetCardFromSerial(data)
        self._currentcard = c
        if c.GetCardPosition() == POS_HAND:
            self.OnCardHandToStack4()
        elif c.GetCardPosition() == POS_FIELD:
            self.OnCardFieldToStack4()
        elif c.GetCardPosition() == POS_DECK:
            self.OnCardDeckToStack4()
        elif c.GetCardPosition() == POS_RFG:
            self.OnCardRFGToStack4()
        elif c.GetCardPosition() == POS_FUSIONDECK:
            self.OnCardFusionDeckToStack4()
 
    def OnCardDropOnStack5(self, x, y, data):
        c = self.GetCardFromSerial(data)
        self._currentcard = c
        if c.GetCardPosition() == POS_HAND:
            self.OnCardHandToStack5()
        elif c.GetCardPosition() == POS_FIELD:
            self.OnCardFieldToStack5()
        elif c.GetCardPosition() == POS_DECK:
            self.OnCardDeckToStack5()
        elif c.GetCardPosition() == POS_RFG:
            self.OnCardRFGToStack5()
        elif c.GetCardPosition() == POS_FUSIONDECK:
            self.OnCardFusionDeckToStack5()
    
    def OnCardDropOnDeck(self, x, y, data):
        c = self.GetCardFromSerial(data)
        self._currentcard = c
        if c.GetCardPosition() == POS_HAND:
            self.OnCardHandToDeck()
        elif c.GetCardPosition() == POS_FIELD:
            self.OnCardFieldToDeck()
        elif c.GetCardPosition() == POS_DECK:
            self.OnCardDeckToDeck()
        elif c.GetCardPosition() == POS_RFG:
            self.OnCardRFGToDeck()
        elif c.GetCardPosition() == POS_FUSIONDECK:
            self.OnCardFusionDeckToDeck()
        elif c.GetCardPosition() == POS_SIDEDECK:
            self.OnCardSideDeckToDeck()

    def OnCardDropOnRFG(self, x, y, data):
        c = self.GetCardFromSerial(data)
        self._currentcard = c
        if c.GetCardPosition() == POS_HAND:
            self.OnCardHandToRFG()
        elif c.GetCardPosition() == POS_FIELD:
            self.OnCardFieldToRFG()
        elif c.GetCardPosition() == POS_DECK:
            self.OnCardDeckToRFG()
        elif c.GetCardPosition() == POS_GRAVE:
            self.OnCardGraveToRFG()
        elif c.GetCardPosition() == POS_FUSIONDECK:
            self.OnCardFusionDeckToRFG()

    def OnCardDropOnHand(self, x, y, data):
        c = self.GetCardFromSerial(data)
        self._currentcard = c
        if c.GetCardPosition() == POS_FIELD and not c.IsFusion():
            self.OnCardFieldToHand()
        elif c.GetCardPosition() == POS_GRAVE:
            self.OnCardGraveToHand()
        elif c.GetCardPosition() == POS_RFG:
            self.OnCardRFGToHand()
        elif c.GetCardPosition() == POS_DECK:
            self.OnCardDeckToHand()
        elif c.GetCardPosition() == POS_STACK_1:
            self.OnCardStack_1_ToHand()
        elif c.GetCardPosition() == POS_STACK_2:
            self.OnCardStack_2_ToHand()
        elif c.GetCardPosition() == POS_STACK_3:
            self.OnCardStack_3_ToHand()
        elif c.GetCardPosition() == POS_STACK_4:
            self.OnCardStack_4_ToHand()
        elif c.GetCardPosition() == POS_STACK_5:
            self.OnCardStack_5_ToHand()

    def OnCardDropOnFusionDeck(self, x, y, data):
        c = self.GetCardFromSerial(data)
        self._currentcard = c
        if c.GetCardPosition() == POS_FUSIONDECK:
            return
        elif c.GetCardPosition() == POS_FIELD:
            self.OnCardFieldToFusionDeck()
        elif c.GetCardPosition() == POS_GRAVE:
            self.OnCardGraveToFusionDeck()
        elif c.GetCardPosition() == POS_RFG:
            self.OnCardRFGToFusionDeck()
    
    def OnCardDropOnSideDeck(self, x, y, data):
        c = self.GetCardFromSerial(data)
        self._currentcard = c
        if c.GetCardPosition() == POS_SIDEDECK:
            return
        elif c.GetCardPosition() == POS_FIELD:
            return
        elif c.GetCardPosition() == POS_GRAVE:
            return
        elif c.GetCardPosition() == POS_RFG:
            return
        elif c.GetCardPosition() == POS_FUSIONDECK:
            return
        elif c.GetCardPosition() == POS_DECK:
            self.OnCardDeckToSideDeck()
        elif c.GetCardPosition() == POS_SIDEDECK:
            self.OnCardSideDeckToDeck()
 
    def RefreshFusionDeck(self):
        l = self._fusiondeck
        n = len(l)
        self._extradeckcounttext.SetLabel(str(len(self._fusiondeck)))
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        self._fusiondecklistctrl.Scroll.Scroll(0,0)
        xtmp = 0
        ytmp = 0
        for c in l:
            if xtmp == 5:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._fusiondecklistctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._fusiondecklistctrl.Scroll.SetScrollbars(0, 20, 0, n)
  
    def RefreshSideDeck(self):
        l = self._sidedeck
        n = len(l)
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        self._sidedecklistctrl.Scroll.Scroll(0,0)
        xtmp = 0
        ytmp = 0
        for c in l:
            if xtmp == 5:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._sidedecklistctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._sidedecklistctrl.Scroll.SetScrollbars(0, 20, 0, n)

    def RefreshOpponentFusionDeck(self):
        l = self._opponentfusiondeck
        n = len(l)
        self._oppextradeckcounttext.SetLabel(str(len(self._opponentfusiondeck)))
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        self._opponentfusiondecklistctrl.Scroll.Scroll(0,0)
        xtmp = 0
        ytmp = 0
        for c in l:
            if xtmp == 5:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._opponentfusiondecklistctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._opponentfusiondecklistctrl.Scroll.SetScrollbars(0, 20, 0, n)
        
    def RefreshOpponentSideDeck(self):
        l = self._opponentsidedeck
        n = len(l)
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        self._opponentsidedecklistctrl.Scroll.Scroll(0,0)
        xtmp = 0
        ytmp = 0
        for c in l:
            if xtmp == 5:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._opponentsidedecklistctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._opponentsidedecklistctrl.Scroll.SetScrollbars(0, 20, 0, n)
        
    '''def RefreshGrave(self):
        self._gravectrl.UpdateCardTooltip(self._grave)
        l = self._grave
        n = len(l)
        if n == 0:
            return
        y_pos = 0
        y_move = 12
        self._gravelistctrl.Scroll.Scroll(0,0)
        for c in l:
            c.RefreshTexture()
            c.SetPosition((0,y_pos))
            c.Reparent(self._gravelistctrl.Scroll)
            c.Hide()
            c.Show()
            y_pos += y_move
        self._gravelistctrl.Scroll.SetScrollbars(0, 12, 0, n)'''

    def RefreshGrave(self):
        self._gravectrl.UpdateCardTooltip(self._grave)
        l = self._grave
        n = len(l)
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        xtmp = 0
        ytmp = 0
        self._gravelistctrl.Scroll.Scroll(0,0)
        for c in l:
            if xtmp == 10:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._gravelistctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._gravelistctrl.Scroll.SetScrollbars(0, 11, 0, n)
    
    def RefreshStack1(self):
        self._stack1ctrl.UpdateCardTooltip(self._stack1)
        l = self._stack1
        n = len(l)
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        xtmp = 0
        ytmp = 0
        self._stack_1_listctrl.Scroll.Scroll(0,0)
        for c in l:
            if xtmp == 3:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._stack_1_listctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._stack_1_listctrl.Scroll.SetScrollbars(0, 30, 0, n)
    
    def RefreshStack2(self):
        self._stack2ctrl.UpdateCardTooltip(self._stack2)
        l = self._stack2
        n = len(l)
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        xtmp = 0
        ytmp = 0
        self._stack_2_listctrl.Scroll.Scroll(0,0)
        for c in l:
            if xtmp == 3:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._stack_2_listctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._stack_2_listctrl.Scroll.SetScrollbars(0, 30, 0, n)
    
    def RefreshStack3(self):
        self._stack3ctrl.UpdateCardTooltip(self._stack3)
        l = self._stack3
        n = len(l)
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        xtmp = 0
        ytmp = 0
        self._stack_3_listctrl.Scroll.Scroll(0,0)
        for c in l:
            if xtmp == 3:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._stack_3_listctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._stack_3_listctrl.Scroll.SetScrollbars(0, 30, 0, n)
    
    def RefreshStack4(self):
        self._stack4ctrl.UpdateCardTooltip(self._stack4)
        l = self._stack4
        n = len(l)
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        xtmp = 0
        ytmp = 0
        self._stack_4_listctrl.Scroll.Scroll(0,0)
        for c in l:
            if xtmp == 3:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._stack_4_listctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._stack_4_listctrl.Scroll.SetScrollbars(0, 30, 0, n)
    
    def RefreshStack5(self):
        self._stack5ctrl.UpdateCardTooltip(self._stack5)
        l = self._stack5
        n = len(l)
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        xtmp = 0
        ytmp = 0
        self._stack_5_listctrl.Scroll.Scroll(0,0)
        for c in l:
            if xtmp == 3:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._stack_5_listctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._stack_5_listctrl.Scroll.SetScrollbars(0, 30, 0, n)
        
    def RefreshOpponentGrave(self):
        self._opponentgravectrl.UpdateCardTooltip(self._opponentgrave)
        l = self._opponentgrave
        n = len(l)
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        xtmp = 0
        ytmp = 0
        self._opponentgravelistctrl.Scroll.Scroll(0,0)
        for c in l:
            if xtmp == 10:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._opponentgravelistctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._opponentgravelistctrl.Scroll.SetScrollbars(0, 11, 0, n)

    def RefreshRFG(self):
        self._rfgctrl.UpdateCardTooltip(self._rfg)
        l = self._rfg
        n = len(l)
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        xtmp = 0
        ytmp = 0
        self._rfglistctrl.Scroll.Scroll(0,0)
        for c in l:
            if xtmp == 10:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._rfglistctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._rfglistctrl.Scroll.SetScrollbars(0, 11, 0, n)

    def RefreshOpponentRFG(self):
        l = self._opponentrfg
        self._opponentrfgctrl.UpdateCardTooltip(self._opponentrfg)
        n = len(l)
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        xtmp = 0
        ytmp = 0
        self._opponentrfglistctrl.Scroll.Scroll(0,0)
        for c in l:
            if xtmp == 10:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._opponentrfglistctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._opponentrfglistctrl.Scroll.SetScrollbars(0, 11, 0, n)

    
    def RefreshDeck(self):
        l = self._deck
        n = len(l)
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        self._decklistctrl.Scroll.Scroll(0,0)
        xtmp = 0
        ytmp = 0
        for c in l:
            if xtmp == 10:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._decklistctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._decklistctrl.Scroll.SetScrollbars(0, 11, 0, n)
        self._deckcounttext.SetLabel(str(len(self._deck)))


    def RefreshOpponentDeck(self):
        l = self._opponentdeck
        n = len(l)
        if n == 0:
            return
        x_pos = 0
        x_move = 64
        y_pos = 0
        y_move = 90
        xtmp = 0
        ytmp = 0
        self._opponentdecklistctrl.Scroll.Scroll(0,0)
        for c in l:
            if xtmp == 10:
                xtmp = 0
                ytmp = ytmp+1
            c.RefreshTexture()
            c.SetPosition((x_move*xtmp,ytmp*y_move))
            c.Reparent(self._opponentdecklistctrl.Scroll)
            c.Hide()
            c.Show()
            xtmp= xtmp+1
        self._opponentdecklistctrl.Scroll.SetScrollbars(0, 11, 0, n)
        self._oppdeckcounttext.SetLabel(str(len(self._opponentdeck)))

    def RefreshHand(self):
        l = self._hand
        n = len(l)
        if n < 1:
            return
        self._handctrl.Show()
        card_width = self.GetCardSize().GetWidth() + 2
        self_width = self._handctrl.GetSize().GetWidth()
        self_mid = self_width/2
        x_pos = 0
        if n > 10:
            card_width = self_width/n
        elif n%2 == 0:
            x_pos = self_mid - (card_width*(n/2))
        else:
            x_pos = self_mid - ((card_width*(n/2)) + card_width/2)
        for c in l:
            c.SetPosition((x_pos,0))
            x_pos += card_width
            c.Hide()
            c.Show()
            if sys.platform == "win32":
                c.Lower()

    def RefreshOpponentHand(self):
        l = self._opponenthand
        n = len(l)
        if n < 1:
            return
        card_width = self.GetCardSize().GetWidth() + 2
        self_width = self._handctrl.GetSize().GetWidth()
        self_mid = self_width/2
        x_pos = 0
        if n > 10:
            card_width = self_width/n
        elif n%2 == 0:
            x_pos = self_mid - (card_width*(n/2))
        else:
            x_pos = self_mid - ((card_width*(n/2)) + card_width/2)
        for c in l:
            c.SetPosition((x_pos,0))
            x_pos += card_width
            c.Hide()
            c.Show()
            if sys.platform == "win32":
                c.Lower()

    def Hit(self, x1, y1, r):
        x2 = r.GetX()
        y2 = r.GetY()
        x3 = r.GetX() + r.GetWidth()
        y3 = r.GetY() + r.GetHeight()
        if x1 >= x2 and x1 <= x3 and y1 >= y2 and y1 <= y3:
            return True
        else:
            return False

    def RefreshCardInfo(self, name, bmp, desc, attrib, type2, stars, typecf, typecm):
        self._cardnamectrl.SetLabel(name)
        self._cardimagectrl.SetBitmap(bmp)
        self._carddescriptionctrl.SetValue(desc)
        self._cardtypectrl.SetBitmap(self._engine.GetSkinImage(typecm))
        self._cardattributectrl.SetBitmap(self._engine.GetSkinImage(attrib))
        if len(type2) > 0:
            self._cardtype2ctrl.SetBitmap(self._engine.GetSkinImage(type2))
        else:
            self._cardtype2ctrl.SetBitmap(self._engine.GetSkinImage('blank'))
        self._cardstarsctrl.SetLabel(stars)
        if typecf == 'Tuner':
            self._cardstarsctrl.SetForegroundColour((0,145,0))
        else:
            self._cardstarsctrl.SetForegroundColour((0,0,0))
        if typecf == 'Exceed':
            self._cardstarsctrl.SetForegroundColour((0,0,255))
        else:
            self._cardstarsctrl.SetForegroundColour((0,0,0))
                
        if attrib == 'Spell' or attrib == 'Trap':
            self._cardstarsctrl.SetLabel('')
            self._cardtypectrl.SetBitmap(self._engine.GetSkinImage('blank'))
            

  
    def RollDice(self, faces):
        n = random.randint(1,int(faces))
        self.WriteRollPacket(faces, n)
        self.WriteGameMessage('rolled a d%s: %s.' % (faces, n), CHAT_PLAYER)

    def RollD6(self, event=None):
        self.RollDice(6)

    def FlipCoin(self, event=None):
        head = random.randint(0,1)
        self.WriteFlipCoinPacket(head)
        if head:
            self.WriteGameMessage(self._engine.GetLangString('flipped a coin : Heads'), CHAT_PLAYER)
        else:
            self.WriteGameMessage(self._engine.GetLangString('flipped a coin : Tails'), CHAT_PLAYER)

    def NextPhase(self):
        if self._drawphasectrl.IsSelected():
            self._standbyphasectrl.OnLeftUp()
        elif self._standbyphasectrl.IsSelected():
            self._mainphase1ctrl.OnLeftUp()
        elif self._mainphase1ctrl.IsSelected():
            self._battlephasectrl.OnLeftUp()
        elif self._battlephasectrl.IsSelected():
            self._mainphase2ctrl.OnLeftUp()
        elif self._mainphase2ctrl.IsSelected():
            self._endphasectrl.OnLeftUp()
        else:
            self._drawphasectrl.OnLeftUp()

    def EndTurn(self):
        self._endphasectrl.OnLeftUp()

    def OnPopupRollD6(self, event=None):
        self.RollDice(6)

    def OnPopupFlipCoin(self, event=None):
        self.FlipCoin()

    def WriteSmiles(self, msg):
        for smile in self._smiles:
            msg = msg.replace(':%s:' % smile, '<img src=%s>' % self._engine.GetSmile(smile))
        return msg

    '''def WriteMessage(self, msg):
        self._messagetext = msg + '<br>' + self._messagetext
        self._messagectrl.SetPage(self._messagetext)'''

    '''def WriteChatMessage(self, msg, w):
        msg = self.WriteSmiles(msg)
        if w == CHAT_PLAYER:
            self._messagetext = '<font color="Blue">' + self._nick + ': ' + '</font>' + msg.decode('utf-8') + '<br>' + self._messagetext
        elif w == CHAT_OPPONENT:
            self._messagetext = '<font color="Red">' + self._opponentnick + ': ' + '</font>' + msg.decode('utf-8') + '<br>' + self._messagetext
        self._messagectrl.SetPage(self._messagetext)
    '''

    def WriteMessage(self, msg):
        self._messagectrl.SetInsertionPointEnd()
        self._messagectrl.Newline()
        self._messagectrl.BeginTextColour(wx.BLACK)
        self._messagectrl.WriteText(msg)
        self._messagectrl.EndTextColour()
        self._messagectrl.SetInsertionPoint(0)
        while self._messagectrl.ScrollLines(10):
            pass
        
        #self._messagectrl.AppendToPage('<br>'+ msg)
        #self._messagectrl.Scroll(0,32001)
        
        #self._messagetext += '<br>' + msg
        #self._messagectrl.SetPage(self._messagetext)
        #self._messagectrl.Scroll(0,int(self._messagectrl.GetScrollPixelsPerUnit()[0]*self._messagetext.count('<br>')))

    def WriteChatMessage(self, msg, w):
        #msg = self.WriteSmiles(msg)

        self._messagectrl.SetInsertionPointEnd()
        self._messagectrl.Newline()
        if w == CHAT_PLAYER:
            self._messagectrl.BeginTextColour(wx.BLUE)
            self._messagectrl.WriteText(self._nick+': ')
            self._messagectrl.EndTextColour()
        elif w == CHAT_OPPONENT:
            self._messagectrl.BeginTextColour(wx.RED)
            self._messagectrl.WriteText(self._opponentnick+': ')
            self._messagectrl.EndTextColour()

        # Metodo per il parsing degli smiles :)
        self._messagectrl.BeginTextColour(wx.BLACK)
        i = 0
        while 1:
            if i >= len(msg):
                break
            w = 1
            if msg[i] == ':':
                for smile in self._smiles:
                    sl = len(smile)
                    if msg[i+1:i+1+len(smile)] == smile:
                        self._messagectrl.WriteImageFile(self._engine.GetSmile(smile), wx.BITMAP_TYPE_GIF)
                        i += len(smile)+1
                        w = 0
                        break
            if w:
                self._messagectrl.WriteText(msg[i])
                i += 1
        self._messagectrl.EndTextColour()

        while self._messagectrl.ScrollLines(10):
            pass
        self._messagectrl.SetInsertionPoint(0)
            
            #msg = '<br><font color="Blue">' + self._nick + ': ' + '</font>' + msg
            
            #msg = '<br><font color="Red">' + self._opponentnick + ': ' + '</font>' + msg.decode('utf-8')
            #msg = '<br><font color="Red">' + self._opponentnick + ': ' + '</font>' + msg
        #self._messagectrl.AppendToPage(msg)
        #self._messagectrl.Scroll(0,32001)
        #if w == CHAT_PLAYER:
        #    self._messagetext += '<br><font color="Blue">' + self._nick + ': ' + '</font>' + msg.decode('utf-8')
        #elif w == CHAT_OPPONENT:
        #    self._messagetext += '<br><font color="Red">' + self._opponentnick + ': ' + '</font>' + msg.decode('utf-8')
        #self._messagectrl.SetPage(self._messagetext)
        #self._messagectrl.Scroll(0,int(self._messagectrl.GetScrollPixelsPerUnit()[0]*self._messagetext.count('<br>')))

    def WriteGameMessage(self, msg, s):
        self._messagectrl.SetInsertionPointEnd()
        self._messagectrl.Newline()
        self._messagectrl.BeginTextColour(wx.GREEN)
        self._messagectrl.WriteText('Game: ')
        self._messagectrl.EndTextColour()
        if s == CHAT_GAME:
            self._messagectrl.BeginTextColour(wx.BLACK)
            self._messagectrl.WriteText(msg)
            self._messagectrl.EndTextColour()
        elif s == CHAT_PLAYER:
            self._messagectrl.BeginTextColour(wx.BLUE)
            self._messagectrl.WriteText(self._nick)
            self._messagectrl.EndTextColour()
            self._messagectrl.BeginTextColour(wx.BLACK)
            self._messagectrl.WriteText(' ' + msg)
            self._messagectrl.EndTextColour()
        elif s == CHAT_OPPONENT:
            self._messagectrl.BeginTextColour(wx.RED)
            self._messagectrl.WriteText(self._opponentnick)
            self._messagectrl.EndTextColour()
            self._messagectrl.BeginTextColour(wx.BLACK)
            self._messagectrl.WriteText(' ' + msg)
            self._messagectrl.EndTextColour()
        elif s == CHAT_CONSOLE:
            self._messagectrl.BeginTextColour(wx.BLACK)
            self._messagectrl.WriteText(msg)
            self._messagectrl.EndTextColour()
        while self._messagectrl.ScrollLines(10):
            pass
        self._messagectrl.SetInsertionPoint(0)

    def ProcessMessage(self, m):
        if m[0] == '/':
            self.ProcessCommand(m[1:])
        else:
            self.WriteChatPacket(m)
            self.WriteChatMessage(m, CHAT_PLAYER)

    def ProcessCommand(self, cmd):
        cmd = cmd
        args = self.GetArgs(cmd)
        cmd = args.pop(0)
        if self._cmdhandlers.has_key(cmd):
            self._cmdhandlers[cmd](args)
        else:
            self.WriteGameMessage("unknown command '" + cmd + "'", CHAT_CONSOLE)

    def GetArgs(self, cmd):
        args = []
        for a in cmd.split(' '):
            args.append(a)
        return args

    def CommandHandlers(self):
        self._cmdhandlers['print'] = self.OnCmdPrint
        self._cmdhandlers['roll'] = self.OnCmdRoll
        self._cmdhandlers['lp'] = self.OnCmdLP
    

    def OnCmdPrint(self, args):
        if len(args) < 1:
            return
        else:
            self.WriteMessage(args[0])
    
    def OnCmdRoll(self, args):
        try:
            faces = int(args[0])
        except:
            self.WriteMessage('Argument error.')
        finally:
            self.RollDice(faces)
    
    def OnCmdLP(self, args):
        try:
            faces = int(args[0])
        except:
            self.WriteMessage('Argument error.')
        finally:
            self._scorectrl.SetPlayerScoreDiff(faces)
    
    def OnClose(self, event=None):
        self.WriteDisconnectPacket()
        self._engine.Network.Close()
        return True

    def GetCardSize(self):
        return self._cardsize

    def GetHand(self):
        return self._hand.GetCards()

    def RefreshCardPosition(self, pos):
        if pos == POS_HAND:
            self.RefreshHand()
        elif pos == POS_GRAVE:
            self.RefreshGrave()()
        elif pos == POS_DECK:
            self.RefreshDeck()
        elif pos == POS_RFG:
            self.RefreshRFG()
        elif pos == POS_STACK_1:
            self.RefreshStack1()
        elif pos == POS_STACK_2:
            self.RefreshStack2()
        elif pos == POS_STACK_3:
            self.RefreshStack3()
        elif pos == POS_STACK_4:
            self.RefreshStack4()
        elif pos == POS_STACK_5:
            self.RefreshStack5()


    def GetCardList(self, pos):
        if pos == POS_FIELD:
            return self._field
        elif pos == POS_HAND:
            return self._hand
        elif pos == POS_GRAVE:
            return self._grave
        elif pos == POS_STACK_1:
            return self._stack1
        elif pos == POS_STACK_2:
            return self._stack2
        elif pos == POS_STACK_3:
            return self._stack3
        elif pos == POS_STACK_4:
            return self._stack4
        elif pos == POS_STACK_5:
            return self._stack5
        elif pos == POS_DECK:
            return self._deck
        elif pos == POS_RFG:
            return self._rfg
        elif pos == POS_OPP_FIELD:
            return self._opponentfield
        elif pos == POS_OPP_HAND:
            return self._opponenthand
        elif pos == POS_OPP_GRAVE:
            return self._opponentgrave
        elif pos == POS_OPP_DECK:
            return self._opponentdeck
        elif pos == POS_OPP_RFG:
            return self._opponentrfg
        return -1

    def GetCardFromSerial(self, serial):
        for c in self._grave:
            if c.GetSerial() == serial:
                return c
        for c in self._stack1:
            if c.GetSerial() == serial:
                return c
        for c in self._stack2:
            if c.GetSerial() == serial:
                return c
        for c in self._stack3:
            if c.GetSerial() == serial:
                return c
        for c in self._stack4:
            if c.GetSerial() == serial:
                return c
        for c in self._stack5:
            if c.GetSerial() == serial:
                return c
        for c in self._field:
            if c.GetSerial() == serial:
                return c
        for c in self._hand:
            if c.GetSerial() == serial:
                return c
        for c in self._deck:
            if c.GetSerial() == serial:
                return c
        for c in self._rfg:
            if c.GetSerial() == serial:
                return c
        for c in self._fusiondeck:
            if c.GetSerial() == serial:
                return c
        for c in self._sidedeck:
            if c.GetSerial() == serial:
                return c

        return -1

    def NewCardSerial(self):
        s = str(self._serial)
        self._serial += 1
        return s

    def GetOpponentCardFromSerial(self, serial):
        for c in self._opponentgrave:
            if c.GetSerial() == serial:
                return c
        for c in self._opponentfield:
            if c.GetSerial() == serial:
                return c
        for c in self._opponenthand:
            if c.GetSerial() == serial:
                return c
        for c in self._opponentdeck:
            if c.GetSerial() == serial:
                return c
        for c in self._opponentrfg:
            if c.GetSerial() == serial:
                return c
        for c in self._opponentfusiondeck:
            if c.GetSerial() == serial:
                return c
        for c in self._opponentsidedeck:
            if c.GetSerial() == serial:
                return c
        return -1

    def NewOpponentCardSerial(self):
        s = str(self._opponentserial)
        self._opponentserial += 1
        return s

    def MoveCard(self, source, dest, card):
        self.MoveCardToTop(source, dest, card)

    def MoveCardToTop(self, source, dest, card):
        source.remove(card)
        dest.insert(0, card)

    def MoveCardToBottom(self, source, dest, card):
        source.remove(card)
        dest.append(card)

    def MoveCardTo(self, source, dest, card, pos):
        source.remove(card)
        dest.insert(pos, card)

    def AddCardTo(self, l, c, n):
        l.insert(n, c)

    def AddCardToTop(self, l, c):
        l.insert(0, c)

    def AddCardToBottom(self, l, c):
        l.append(c)

    def AddCardListToBottom(self, l, o):
        o.reverse()
        for c in o:
            l.append(c)

    def AddCardListToTop(self, l, o):
        o.reverse()
        for c in o:
            l.insert(0, c)
    
    def RemoveCard(self, l, c):
        l.remove(c)

    def RemoveCardFrom(self, l, n):
        return l.pop(n)

    def RemoveCardFromTop(self, l):
        return l.pop(0)

    def RemoveCardFromBottom(self, l):
        return l.pop(len(l)-1)

    def Shuffle(self):
        random.shuffle(self._deck)
        self.RefreshDeck()
        self.WriteGameMessage(self._engine.GetLangString('shuffled his deck.'), CHAT_PLAYER)
        self.WriteShufflePacket()
        self._deckcounttext.SetLabel(str(len(self._deck)))
    
    def ShuffleHand(self):
        random.shuffle(self._hand)
        self.RefreshHand()
        self.WriteGameMessage(self._engine.GetLangString('shuffled his hand.'), CHAT_PLAYER)
        self.WriteShuffleHandPacket()

    def ResetGame(self):
        while len(self._field) > 0:
            c = self._field[0]
            if c.IsFusion() or c.IsSynchro() or c.IsToken():
                self.MoveCard(self._field, self._fusiondeck, c)
                c.SetCardState(POS_FUSIONDECK)
                c.Reparent(self._fusiondecklistctrl)
                c.Hide()
                c.Show()
            else:
                self.MoveCard(self._field, self._deck, c)
                c.SetCardState(POS_DECK)
                c.Reparent(self._decklistctrl)
                c.Hide()
                c.Show()
        while len(self._grave) > 0:
            c = self._grave[0]
            if c.IsFusion() or c.IsSynchro() or c.IsToken():
                self.MoveCard(self._grave, self._fusiondeck, c)
                c.SetCardState(POS_FUSIONDECK)
                c.Reparent(self._fusiondecklistctrl)
                c.Hide()
                c.Show()
            else:
                self.MoveCard(self._grave, self._deck, c)
                c.SetCardState(POS_DECK)
                c.Reparent(self._decklistctrl)
                c.Hide()
                c.Show()
        while len(self._stack1) > 0:
            c = self._stack1[0]
            if c.IsFusion() or c.IsSynchro() or c.IsToken():
                self.MoveCard(self._stack1, self._fusiondeck, c)
                c.SetCardState(POS_FUSIONDECK)
                c.Reparent(self._fusiondecklistctrl)
                c.Hide()
                c.Show()
            else:
                self.MoveCard(self._stack1, self._deck, c)
                c.SetCardState(POS_DECK)
                c.Reparent(self._decklistctrl)
                c.Hide()
                c.Show()
        while len(self._stack2) > 0:
            c = self._stack1[0]
            if c.IsFusion() or c.IsSynchro() or c.IsToken():
                self.MoveCard(self._stack2, self._fusiondeck, c)
                c.SetCardState(POS_FUSIONDECK)
                c.Reparent(self._fusiondecklistctrl)
                c.Hide()
                c.Show()
            else:
                self.MoveCard(self._stack2, self._deck, c)
                c.SetCardState(POS_DECK)
                c.Reparent(self._decklistctrl)
                c.Hide()
                c.Show()
        while len(self._stack3) > 0:
            c = self._stack1[0]
            if c.IsFusion() or c.IsSynchro() or c.IsToken():
                self.MoveCard(self._stack3, self._fusiondeck, c)
                c.SetCardState(POS_FUSIONDECK)
                c.Reparent(self._fusiondecklistctrl)
                c.Hide()
                c.Show()
            else:
                self.MoveCard(self._stack3, self._deck, c)
                c.SetCardState(POS_DECK)
                c.Reparent(self._decklistctrl)
                c.Hide()
                c.Show()
        while len(self._stack4) > 0:
            c = self._stack1[0]
            if c.IsFusion() or c.IsSynchro() or c.IsToken():
                self.MoveCard(self._stack4, self._fusiondeck, c)
                c.SetCardState(POS_FUSIONDECK)
                c.Reparent(self._fusiondecklistctrl)
                c.Hide()
                c.Show()
            else:
                self.MoveCard(self._stack4, self._deck, c)
                c.SetCardState(POS_DECK)
                c.Reparent(self._decklistctrl)
                c.Hide()
                c.Show()
        while len(self._stack5) > 0:
            c = self._stack1[0]
            if c.IsFusion() or c.IsSynchro() or c.IsToken():
                self.MoveCard(self._stack5, self._fusiondeck, c)
                c.SetCardState(POS_FUSIONDECK)
                c.Reparent(self._fusiondecklistctrl)
                c.Hide()
                c.Show()
            else:
                self.MoveCard(self._stack5, self._deck, c)
                c.SetCardState(POS_DECK)
                c.Reparent(self._decklistctrl)
                c.Hide()
                c.Show()
        while len(self._rfg) > 0:
            c = self._rfg[0]
            if c.IsFusion() or c.IsSynchro() or c.IsToken():
                self.MoveCard(self._rfg, self._fusiondeck, c)
                c.SetCardState(POS_FUSIONDECK)
                c.Reparent(self._fusiondecklistctrl)
                c.Hide()
                c.Show()
            else:
                self.MoveCard(self._rfg, self._deck, c)
                c.SetCardState(POS_DECK)
                c.Reparent(self._decklistctrl)
                c.Hide()
                c.Show()
        while len(self._hand) > 0:
            c = self._hand[0]
            if c.IsFusion() or c.IsSynchro() or c.IsToken():
                self.MoveCard(self._hand, self._fusiondeck, c)
                c.SetCardState(POS_FUSIONDECK)
                c.Reparent(self._fusiondecklistctrl)
                c.Hide()
                c.Show()
            else:
                self.MoveCard(self._hand, self._deck, c)
                c.SetCardState(POS_DECK)
                c.Reparent(self._decklistctrl)
                c.Hide()
                c.Show()
        self.RefreshAll()
        self.WriteGameMessage('Game Reset.', CHAT_PLAYER)
        self._scorectrl.SetPlayerScore(8000)
        self.WriteResetGamePacket()
        self.Shuffle()

    def ResetOpponentGame(self):
        while len(self._opponentfield) > 0:
            c = self._opponentfield[0]
            if c.IsFusion() or c.IsSynchro() or c.IsToken():
                self.MoveCard(self._opponentfield, self._opponentfusiondeck, c)
                c.SetCardState(POS_OPP_FUSIONDECK)
                c.Reparent(self._opponentfusiondecklistctrl)
                c.Hide()
                c.Show()
            else:
                self.MoveCard(self._opponentfield, self._opponentdeck, c)
                c.SetCardState(POS_OPP_DECK)
                c.Reparent(self._opponentdecklistctrl)
                c.Hide()
                c.Show()
        while len(self._opponentgrave) > 0:
            c = self._opponentgrave[0]
            if c.IsFusion() or c.IsSynchro() or c.IsToken():
                self.MoveCard(self._opponentgrave, self._opponentfusiondeck, c)
                c.SetCardState(POS_OPP_FUSIONDECK)
                c.Reparent(self._opponentfusiondecklistctrl)
                c.Hide()
                c.Show()
            else:
                self.MoveCard(self._opponentgrave, self._opponentdeck, c)
                c.SetCardState(POS_OPP_DECK)
                c.Reparent(self._opponentdecklistctrl)
                c.Hide()
                c.Show()
        while len(self._opponentrfg) > 0:
            c = self._opponentrfg[0]
            if c.IsFusion() or c.IsSynchro() or c.IsToken():
                self.MoveCard(self._opponentrfg, self._opponentfusiondeck, c)
                c.SetCardState(POS_OPP_FUSIONDECK)
                c.Reparent(self._opponentfusiondecklistctrl)
                c.Hide()
                c.Show()
            else:
                self.MoveCard(self._opponentrfg, self._opponentdeck, c)
                c.SetCardState(POS_OPP_DECK)
                c.Reparent(self._opponentdecklistctrl)
                c.Hide()
                c.Show()
        while len(self._opponenthand) > 0:
            c = self._opponenthand[0]
            if c.IsFusion() or c.IsSynchro() or c.IsToken():
                self.MoveCard(self._opponenthand, self._opponentfusiondeck, c)
                c.SetCardState(POS_OPP_FUSIONDECK)
                c.Reparent(self._opponentfusiondecklistctrl)
                c.Hide()
                c.Show()
            else:
                self.MoveCard(self._opponenthand, self._opponentdeck, c)
                c.SetCardState(POS_OPP_DECK)
                c.Reparent(self._opponentdecklistctrl)
                c.Hide()
                c.Show()
        self.RefreshOpponentAll()
        self._scorectrl.SetOpponentScore(8000)
        self.WriteGameMessage('Game Reset.', CHAT_OPPONENT)

    def RefreshAll(self):
        self.RefreshHand()
        self.RefreshGrave()
        self.RefreshStack1()
        self.RefreshStack2()
        self.RefreshStack3()
        self.RefreshStack4()
        self.RefreshStack5()
        self.RefreshRFG()
        self.RefreshDeck()
        self.RefreshFusionDeck()
        self.RefreshSideDeck()

    def RefreshOpponentAll(self):
        self.RefreshOpponentHand()
        self.RefreshOpponentGrave()
        self.RefreshOpponentRFG()
        self.RefreshOpponentDeck()
        self.RefreshOpponentFusionDeck()
        self.RefreshOpponentSideDeck()

    # Packets
    def WritePacket(self, packet):
        if self._engine.Network.GetState() == network.ID_CONNECTED:
            try:
                self._engine.Network.Write(packet.Build())
            except:
                self.OnDisconnectPacket()

    def WriteChatPacket(self, m):
        self.WritePacket(packets.ChatPacket(m))

    def WriteDeckPacket(self):
        self.WritePacket(packets.DeckPacket(self._origdeck.GetCards()))

    def WriteShufflePacket(self):
        self.WritePacket(packets.ShufflePacket(self._deck))
    
    def WriteShuffleHandPacket(self):
        self.WritePacket(packets.ShuffleHandPacket(self._hand))
    
    def WriteMoveCardPacket(self, card, dest, dest2=0, x=0, y=0):
        x = self._opponentfieldctrl.GetSize().GetWidth() - x
        y = self._opponentfieldctrl.GetSize().GetHeight() - y
        self.WritePacket(packets.CardMovePacket(card.GetSerial(),dest,dest2,x,y))

    def WriteFlipCardPacket(self, card, sta):
        self.WritePacket(packets.CardFlipPacket(card.GetSerial(),sta))
        
    def WriteLifeChangePacket(self, change):
        self.WritePacket(packets.LifeChangePacket(change))
        
    def WritePhasePacket(self, phase):
        self.WritePacket(packets.PhasePacket(phase))
        
    def WriteRollPacket(self, faces, n):
        self.WritePacket(packets.RollPacket(faces, n))
        
    def WriteDisconnectPacket(self):
        self.WritePacket(packets.DisconnectPacket())
        
    def WriteTargetPacket(self, p, serial):
        self.WritePacket(packets.TargetPacket(p, serial))
        
    def WriteFlipCoinPacket(self, h):
        self.WritePacket(packets.FlipCoinPacket(h))
        
    def WriteResetGamePacket(self):
        self.WritePacket(packets.ResetGamePacket())
        
    def WriteLookPacket(self, n):
        self.WritePacket(packets.LookPacket(n))

    def WriteCardActionPacket(self, action):
        self.WritePacket(packets.CardActionPacket(action))

    def WriteCardCounterPacket(self, serial, action, count):
        self.WritePacket(packets.CardCounterPacket(serial, action, count))
    
    def WriteChangeControlPacket(self, serial, action, count):
        self.WritePacket(packets.ChangeControlPacket(serial, action, count))
    
    # Packet Events
    def OnConnectPacket(self, event):
        self.Parent.Show()
        self._opponentnick = event.data.ReadString()
        self._opponentversion = event.data.ReadString()
        self.WriteGameMessage(self._engine.GetLangString('Connected with: ') + self._opponentnick + ' (' + self._opponentversion + ')', CHAT_GAME)
        self.WriteDeckPacket()

    def OnChatPacket(self, event):
        self.WriteChatMessage(': ' + event.data.ReadString(), CHAT_OPPONENT)

    def OnDeckPacket(self, event):
        reader = event.data
        cards = []
        while 1:
            try:
                c = self._engine.FindCardByCode(reader.ReadString())
            except:
                break
            if reader.ReadBool():
                c.IsSide = 1
            cards.append(c)
        self._opponentorigdeck = Deck()
        for c in cards:
            self._opponentorigdeck.Add(c)
        deck = self._opponentorigdeck.GetGameCards()
        side = self._opponentorigdeck.GetSide()
        fusion = self._opponentorigdeck.GetFusions()
        for c in deck:
            g = OpponentCardControl(self._opponentdecklistctrl, c.Duplicate(), self._engine, self, self.NewOpponentCardSerial(), cpos=POS_OPP_DECK)
            self.AddCardToBottom(self._opponentdeck, g)
        for c in side:
            g = OpponentCardControl(self._noneparent, c.Duplicate(), self._engine, self, self.NewOpponentCardSerial(), cpos=POS_OPP_SIDEDECK)
            self.AddCardToBottom(self._opponentsidedeck, g)
        for c in fusion:
            g = OpponentCardControl(self._opponentfusiondecklistctrl, c.Duplicate(), self._engine, self, self.NewOpponentCardSerial(), cpos=POS_OPP_FUSIONDECK)
            self.AddCardToBottom(self._opponentfusiondeck, g)
        self.RefreshOpponentDeck()
        self.Shuffle()

    def OnDrawPacket(self, event):
        reader = event.data
        self.OnOpponentDeckDraw(reader.ReadBool())

    def OnShufflePacket(self, event):
        reader = event.data
        l = []
        while 1:
            try:
                l.append(self.GetOpponentCardFromSerial(reader.ReadString()))
            except:
               break
        self._opponentdeck = l
        self.RefreshOpponentDeck()
        self.WriteGameMessage(self._engine.GetLangString('shuffled his deck.'), CHAT_OPPONENT)

    def OnShuffleHandPacket(self, event):
        reader = event.data
        l = []
        while 1:
            try:
                l.append(self.GetOpponentCardFromSerial(reader.ReadString()))
            except:
               break
        self._opponenthand = l
        self.RefreshOpponentHand()
        self.WriteGameMessage(self._engine.GetLangString('shuffled his hand'), CHAT_OPPONENT)
    
    def OnChangeControlPacket(self, event):
        reader = event.data
        l = []
        while 1:
            try:
                l.append(self.GetOpponentCardFromSerial(reader.ReadString()))
            except:
               break
        self._opponentfield = l
        self.WriteGameMessage(self._engine.GetLangString('Changed Control'), CHAT_OPPONENT)
    
    def OnCardMovePacket(self, event):
        reader = event.data
        card = self.GetOpponentCardFromSerial(reader.ReadString())
        dest = reader.ReadInt()
        self._opponentcurrentcard = card
        pos = card.GetCardPosition()
        if pos == POS_OPP_HAND: # Hand
            if dest == POS_OPP_DECK: # Deck
                dest2 = reader.ReadInt()
                if dest2 == 0: # Bottom Deck
                    self.OnOpponentCardHandToBottomDeck()
                elif dest2 == 1: # Top Deck
                    self.OnOpponentCardHandToTopDeck()
                else: # Deck
                    self.OnOpponentCardHandToDeckShuffle()
            elif dest == POS_OPP_GRAVE: # Grave
                self.OnOpponentCardHandToGrave()
            elif dest == POS_OPP_STACK_1: # Grave
                self.OnOpponentCardHandToStack1()
            elif dest == POS_OPP_STACK_2: 
                self.OnOpponentCardHandToStack2()
            elif dest == POS_OPP_STACK_3: 
                self.OnOpponentCardHandToStack3()
            elif dest == POS_OPP_STACK_4: 
                self.OnOpponentCardHandToStack4()
            elif dest == POS_OPP_STACK_5: 
                self.OnOpponentCardHandToStack5()
            elif dest == POS_OPP_RFG: # RFG
                self.OnOpponentCardHandToRFG()
            elif dest == POS_OPP_FIELD: # Field
                dest2 = reader.ReadInt()
                x = reader.ReadInt()
                y = reader.ReadInt()
                self._opponentcurrentcard = [card,x,y]
                if dest2 == 0: # Vertical Face-Up
                    if card.IsMonster():
                        self.OnOpponentHandMonsterSummon()
                    else:
                        self.OnOpponentHandMTActivate()
                elif dest2 == 1: # Vertical Face-Down
                    self.OnOpponentHandMTPosition()
                else: # Horizontal Face-Down
                    self.OnOpponentHandMonsterPosition()
        elif pos == POS_OPP_FIELD:
            if dest == POS_OPP_HAND:
                self.OnOpponentCardFieldToHand()
            elif dest == POS_OPP_GRAVE:
                self.OnOpponentCardFieldToGrave()
            elif dest == POS_OPP_STACK_1:
                self.OnOpponentCardFieldToStack1()
            elif dest == POS_OPP_STACK_2:
                self.OnOpponentCardFieldToStack2()
            elif dest == POS_OPP_STACK_3:
                self.OnOpponentCardFieldToStack3()
            elif dest == POS_OPP_STACK_4:
                self.OnOpponentCardFieldToStack4()
            elif dest == POS_OPP_STACK_5:
                self.OnOpponentCardFieldToStack5()
            elif dest == POS_OPP_RFG:
                self.OnOpponentCardFieldToRFG()
            elif dest == POS_OPP_DECK:
                dest2 = reader.ReadInt()
                if dest2 == 0:
                    self.OnOpponentCardFieldToBottomDeck()
                elif dest2 == 1:
                    self.OnOpponentCardFieldToTopDeck()
                else:
                    self.OnOpponentCardFieldToDeckShuffle()
            elif dest == POS_OPP_FIELD:
                dest2 = reader.ReadInt()
                x = reader.ReadInt()
                y = reader.ReadInt()
                self._opponentcurrentcard = [card,x,y]
                self.OnOpponentCardFieldMove(card, x, y)
            elif dest == POS_OPP_FUSIONDECK:
                self.OnOpponentCardFieldToFusionDeck()
        elif pos == POS_OPP_GRAVE:
            if dest == POS_OPP_HAND:
                self.OnOpponentCardGraveToHand()
            elif dest == POS_OPP_RFG:
                self.OnOpponentCardGraveToRFG()
            elif dest == POS_OPP_DECK:
                dest2 = reader.ReadInt()
                if dest2 == 0:
                    self.OnOpponentCardGraveToBottomDeck()
                elif dest2 == 1:
                    self.OnOpponentCardGraveToTopDeck()
                elif dest2 == 2:
                    self.OnOpponentCardGraveToDeckShuffle()
            elif dest == POS_OPP_FIELD:
                dest2 = reader.ReadInt()
                x = reader.ReadInt()
                y = reader.ReadInt()
                self._opponentcurrentcard = [card,x,y]
                self.OnOpponentCardGraveToField()
            elif dest == POS_OPP_FUSIONDECK:
                self.OnOpponentCardGraveToFusionDeck()
        elif pos == POS_OPP_STACK_1:
            if dest == POS_OPP_HAND:
                self.OnOpponentCardStack_1_ToHand()
            '''elif dest == POS_OPP_RFG:
                self.OnOpponentCardStack_1_ToRFG()
            elif dest == POS_OPP_DECK:
                dest2 = reader.ReadInt()
                if dest2 == 0:
                    self.OnOpponentCardStack_1_ToBottomDeck()
                elif dest2 == 1:
                    self.OnOpponentCardStack_1_ToTopDeck()
                elif dest2 == 2:
                    self.OnOpponentCardStack_1_ToDeckShuffle()
            elif dest == POS_OPP_FIELD:
                dest2 = reader.ReadInt()
                x = reader.ReadInt()
                y = reader.ReadInt()
                self._opponentcurrentcard = [card,x,y]
                self.OnOpponentCardStack_1_ToField()
            elif dest == POS_OPP_FUSIONDECK:
                self.OnOpponentCardStack_1_ToFusionDeck()'''
        elif pos == POS_OPP_STACK_2:
            if dest == POS_OPP_HAND:
                self.OnOpponentCardStack_2_ToHand()
            '''elif dest == POS_OPP_RFG:
                self.OnOpponentCardStack_2_ToRFG()
            elif dest == POS_OPP_DECK:
                dest2 = reader.ReadInt()
                if dest2 == 0:
                    self.OnOpponentCardStack_2_ToBottomDeck()
                elif dest2 == 1:
                    self.OnOpponentCardStack_2_ToTopDeck()
                elif dest2 == 2:
                    self.OnOpponentCardStack_2_ToDeckShuffle()
            elif dest == POS_OPP_FIELD:
                dest2 = reader.ReadInt()
                x = reader.ReadInt()
                y = reader.ReadInt()
                self._opponentcurrentcard = [card,x,y]
                self.OnOpponentCardStack_2_ToField()
            elif dest == POS_OPP_FUSIONDECK:
                self.OnOpponentCardStack_2_ToFusionDeck()'''
        elif pos == POS_OPP_STACK_3:
            if dest == POS_OPP_HAND:
                self.OnOpponentCardStack_3_ToHand()
            '''elif dest == POS_OPP_RFG:
                self.OnOpponentCardStack_3_ToRFG()
            elif dest == POS_OPP_DECK:
                dest2 = reader.ReadInt()
                if dest2 == 0:
                    self.OnOpponentCardStack_3_ToBottomDeck()
                elif dest2 == 1:
                    self.OnOpponentCardStack_3_ToTopDeck()
                elif dest2 == 2:
                    self.OnOpponentCardStack_3_ToDeckShuffle()
            elif dest == POS_OPP_FIELD:
                dest2 = reader.ReadInt()
                x = reader.ReadInt()
                y = reader.ReadInt()
                self._opponentcurrentcard = [card,x,y]
                self.OnOpponentCardStack_3_ToField()
            elif dest == POS_OPP_FUSIONDECK:
                self.OnOpponentCardStack_3_ToFusionDeck()'''
        elif pos == POS_OPP_STACK_4:
            if dest == POS_OPP_HAND:
                self.OnOpponentCardStack_4_ToHand()
            '''elif dest == POS_OPP_RFG:
                self.OnOpponentCardStack_4_ToRFG()
            elif dest == POS_OPP_DECK:
                dest2 = reader.ReadInt()
                if dest2 == 0:
                    self.OnOpponentCardStack_4_ToBottomDeck()
                elif dest2 == 1:
                    self.OnOpponentCardStack_4_ToTopDeck()
                elif dest2 == 2:
                    self.OnOpponentCardStack_4_ToDeckShuffle()
            elif dest == POS_OPP_FIELD:
                dest2 = reader.ReadInt()
                x = reader.ReadInt()
                y = reader.ReadInt()
                self._opponentcurrentcard = [card,x,y]
                self.OnOpponentCardStack_4_ToField()
            elif dest == POS_OPP_FUSIONDECK:
                self.OnOpponentCardStack_4_ToFusionDeck()'''
        elif pos == POS_OPP_STACK_5:
            if dest == POS_OPP_HAND:
                self.OnOpponentCardStack_5_ToHand()
            '''elif dest == POS_OPP_RFG:
                self.OnOpponentCardStack_5_ToRFG()
            elif dest == POS_OPP_DECK:
                dest2 = reader.ReadInt()
                if dest2 == 0:
                    self.OnOpponentCardStack_5_ToBottomDeck()
                elif dest2 == 1:
                    self.OnOpponentCardStack_5_ToTopDeck()
                elif dest2 == 2:
                    self.OnOpponentCardStack_5_ToDeckShuffle()
            elif dest == POS_OPP_FIELD:
                dest2 = reader.ReadInt()
                x = reader.ReadInt()
                y = reader.ReadInt()
                self._opponentcurrentcard = [card,x,y]
                self.OnOpponentCardStack_5_ToField()
            elif dest == POS_OPP_FUSIONDECK:
                self.OnOpponentCardStack_5_ToFusionDeck()'''
        elif pos == POS_OPP_RFG:
            if dest == POS_OPP_HAND:
                self.OnOpponentCardRFGToHand()
            elif dest == POS_OPP_GRAVE:
                self.OnOpponentCardRFGToGrave()
            elif dest == POS_OPP_DECK:
                dest2 = reader.ReadInt()
                if dest2 == 0:
                    self.OnOpponentCardRFGToBottomDeck()
                elif dest2 == 1:
                    self.OnOpponentCardRFGToTopDeck()
                elif dest2 == 2:
                    self.OnOpponentCardRFGToDeckShuffle()
            elif dest == POS_OPP_FIELD:
                dest2 = reader.ReadInt()
                x = reader.ReadInt()
                y = reader.ReadInt()
                self._opponentcurrentcard = [card,x,y]
                self.OnOpponentCardRFGToField()
            elif dest == POS_OPP_FUSIONDECK:
                self.OnOpponentCardRFGToFusionDeck()
        elif pos == POS_OPP_DECK:
            if dest == POS_OPP_HAND:
                self.OnOpponentCardDeckToHand()
            elif dest == POS_OPP_GRAVE:
                self.OnOpponentCardDeckToGrave()
            elif dest == POS_OPP_RFG:
                self.OnOpponentCardDeckToRFG()
            elif dest == POS_OPP_SIDEDECK:
                self.OnOpponentCardDeckToSideDeck()
            elif dest == POS_OPP_FIELD:
                dest2 = reader.ReadInt()
                x = reader.ReadInt()
                y = reader.ReadInt()
                self._opponentcurrentcard = [card,x,y]
                self.OnOpponentCardDeckToField()
        elif pos == POS_OPP_FUSIONDECK:
            if dest == POS_OPP_GRAVE:
                self.OnOpponentCardFusionDeckToGrave()
            elif dest == POS_OPP_RFG:
                self.OnOpponentCardFusionDeckToRFG()
            elif dest == POS_OPP_FIELD:
                dest2 = reader.ReadInt()
                x = reader.ReadInt()
                y = reader.ReadInt()
                self._opponentcurrentcard = [card,x,y]
                self.OnOpponentCardFusionDeckToField()
        elif pos == POS_OPP_SIDEDECK:
            if dest == POS_OPP_DECK:
                self.OnOpponentCardSideDeckToDeck()
 
    def OnCardFlipPacket(self, event):
        reader = event.data
        card = self.GetOpponentCardFromSerial(reader.ReadString())
        self._opponentcurrentcard = card
        state = reader.ReadInt()
        pos = card.GetCardPosition()
        if pos == POS_OPP_FIELD:
            if state == 0:
                self.OnOpponentCardFieldFlip()
            elif state == 1:
                self.OnOpponentCardFieldFlipHorizontal()
            elif state == 2:
                self.OnOpponentCardFieldFlipVertical()
            elif state == 3:
                self.OnOpponentCardFieldHorizontal()
            elif state == 4:
                self.OnOpponentCardFieldVertical()

    def OnLifeChangePacket(self, event):
        change = event.data.ReadInt()
        self._scorectrl.SetOpponentScoreDiff(change)

    def OnPhasePacket(self, event):
        phase = event.data.ReadInt()
        if phase == 0:
            self._drawphasectrl.SelectPhase()
            self.WriteGameMessage('entered his Draw Phase.', CHAT_OPPONENT)
        elif phase == 1:
            self._standbyphasectrl.SelectPhase()
            self.WriteGameMessage('entered his Standby Phase.', CHAT_OPPONENT)
        elif phase == 2:
            self._mainphase1ctrl.SelectPhase()
            self.WriteGameMessage('entered his Main Phase 1.', CHAT_OPPONENT)
        elif phase == 3:
            self._battlephasectrl.SelectPhase()
            self.WriteGameMessage('entered his Battle Phase.', CHAT_OPPONENT)
        elif phase == 4:
            self._mainphase2ctrl.SelectPhase()
            self.WriteGameMessage('entered his Main Phase 2.', CHAT_OPPONENT)
        elif phase == 5:
            self._endphasectrl.SelectPhase()
            self.WriteGameMessage('end his turn.', CHAT_OPPONENT)

    def OnRollPacket(self, event):
        reader = event.data
        faces = reader.ReadInt()
        n = reader.ReadInt()
        self.WriteGameMessage(self._engine.GetLangString('rolled a d')+str(faces)+': '+str(n), CHAT_OPPONENT)

    def OnDisconnectPacket(self, event=None):
        self.WriteGameMessage('disconnected.', CHAT_OPPONENT)
        self._engine.Network.Close()

    def OnTargetPacket(self, event):
        reader = event.data
        if reader.ReadInt() == 1:
            card = self.GetCardFromSerial(reader.ReadString())
            card.Target()
            card.Hide()
            card.Show()
        else:
            card = self.GetOpponentCardFromSerial(reader.ReadString())
            card.Target()
            card.Hide()
            card.Show()

    def OnFlipCoinPacket(self, event):
        reader = event.data
        head = reader.ReadBool()
        if head:
            self.WriteGameMessage(self._engine.GetLangString('flipped a coin: Heads.'), CHAT_OPPONENT)
        else:
            self.WriteGameMessage(self._engine.GetLangString('flipped a coin: Tails.'), CHAT_OPPONENT)

    def OnResetGamePacket(self, event):
        self.ResetOpponentGame()

    def OnLookPacket(self, event):
        reader = event.data
        n = reader.ReadInt()
        if n == LOOK_DECK_YES:
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Deck'), CHAT_OPPONENT)
            self._opponentdeckctrl.SetTexture(self._engine.GetSkinImage('LookDeck'))
        elif n == LOOK_DECK_NO:
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Deck'), CHAT_OPPONENT)
            self._opponentdeckctrl.SetTexture(self._engine.GetSkinImage('Deck'))
        elif n == LOOK_GRAVE_YES:
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Graveyard'), CHAT_OPPONENT)
        elif n == LOOK_GRAVE_NO:
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Graveyard'), CHAT_OPPONENT)
        elif n == LOOK_STACK_1__YES:
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Stack 1'), CHAT_OPPONENT)
        elif n == LOOK_STACK_1_NO:
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Sack 1'), CHAT_OPPONENT)
        elif n == LOOK_OPP_STACK_1__YES:
            self.WriteGameMessage(self._engine.GetLangString("is looking at his opponent's Stack 1"), CHAT_OPPONENT)
        elif n == LOOK_OPP_STACK_1_NO:
            self.WriteGameMessage(self._engine.GetLangString("end looking at his opponent's Sack 1"), CHAT_OPPONENT)
        elif n == LOOK_STACK_2__YES:
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Stack 2'), CHAT_OPPONENT)
        elif n == LOOK_STACK_2_NO:
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Sack 2'), CHAT_OPPONENT)
        elif n == LOOK_OPP_STACK_2__YES:
            self.WriteGameMessage(self._engine.GetLangString("is looking at his opponent's Stack 2"), CHAT_OPPONENT)
        elif n == LOOK_OPP_STACK_2_NO:
            self.WriteGameMessage(self._engine.GetLangString("end looking at his opponent's Sack 2"), CHAT_OPPONENT)
        elif n == LOOK_STACK_3__YES:
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Stack 3'), CHAT_OPPONENT)
        elif n == LOOK_STACK_3_NO:
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Sack 3'), CHAT_OPPONENT)
        elif n == LOOK_OPP_STACK_3__YES:
            self.WriteGameMessage(self._engine.GetLangString("is looking at his opponent's Stack 3"), CHAT_OPPONENT)
        elif n == LOOK_OPP_STACK_3_NO:
            self.WriteGameMessage(self._engine.GetLangString("end looking at his opponent's Sack 3"), CHAT_OPPONENT)
        elif n == LOOK_STACK_4__YES:
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Stack 4'), CHAT_OPPONENT)
        elif n == LOOK_STACK_4_NO:
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Sack 4'), CHAT_OPPONENT)
        elif n == LOOK_OPP_STACK_4__YES:
            self.WriteGameMessage(self._engine.GetLangString("is looking at his opponent's Stack 4"), CHAT_OPPONENT)
        elif n == LOOK_OPP_STACK_4_NO:
            self.WriteGameMessage(self._engine.GetLangString("end looking at his opponent's Sack 4"), CHAT_OPPONENT)
        elif n == LOOK_STACK_5__YES:
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Stack 5'), CHAT_OPPONENT)
        elif n == LOOK_STACK_5_NO:
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Sack 5'), CHAT_OPPONENT)
        elif n == LOOK_OPP_STACK_5__YES:
            self.WriteGameMessage(self._engine.GetLangString("is looking at his opponent's Stack 5"), CHAT_OPPONENT)
        elif n == LOOK_OPP_STACK_5_NO:
            self.WriteGameMessage(self._engine.GetLangString("end looking at his opponent's Sack 5"), CHAT_OPPONENT)
        elif n == LOOK_RFG_YES:
            self.WriteGameMessage(self._engine.GetLangString('is looking at his RFG'), CHAT_OPPONENT)
        elif n == LOOK_RFG_NO:
            self.WriteGameMessage(self._engine.GetLangString('end looking at his RFG'), CHAT_OPPONENT)
        elif n == LOOK_FUSIONDECK_YES:
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Extra Deck'), CHAT_OPPONENT)
        elif n == LOOK_FUSIONDECK_NO:
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Extra Deck'), CHAT_OPPONENT)
        elif n == LOOK_OPPONENT_GRAVE_YES:
            self.WriteGameMessage(self._engine.GetLangString("is looking at his opponent's Graveyard"), CHAT_OPPONENT)
        elif n == LOOK_OPPONENT_GRAVE_NO:
            self.WriteGameMessage(self._engine.GetLangString("end looking at his opponent's Graveyard"), CHAT_OPPONENT)
        elif n == LOOK_OPPONENT_RFG_YES:
            self.WriteGameMessage(self._engine.GetLangString("is looking at his opponent's RFG"), CHAT_OPPONENT)
        elif n == LOOK_OPPONENT_RFG_NO:
            self.WriteGameMessage(self._engine.GetLangString("end looking at his opponent's RFG"), CHAT_OPPONENT)
        elif n == LOOK_SIDEDECK_YES:
            self.WriteGameMessage(self._engine.GetLangString('is looking at his Side Deck'), CHAT_OPPONENT)
        elif n == LOOK_SIDEDECK_NO:
            self.WriteGameMessage(self._engine.GetLangString('end looking at his Side Deck'), CHAT_OPPONENT)

    def OnCardActionPacket(self, event):
        reader = event.data
        action = reader.ReadInt()
        if action == ACTION_DISCARDTOP:
            self.OnOpponentActionDiscardTop()
        elif action == ACTION_REVEALTOP:
            self.OnOpponentActionRevealTop()

    def OnCardCounterPacket(self, event):
        reader = event.data
        serial = reader.ReadString()
        card = self.GetOpponentCardFromSerial(serial)
        action = reader.ReadInt()
        count = reader.ReadInt()
        if action == 0: # Add Counters
            card.AddCounters(count)
            self.WriteGameMessage(' %s %s' % (self._engine.GetLangString("added a counter to"), card.GetCardName()), CHAT_OPPONENT)
        else: # Remove Counters
            card.RemoveCounters(count)
            self.WriteGameMessage(' %s %s' % (self._engine.GetLangString("removed a counter from"), card.GetCardName()), CHAT_OPPONENT)


class FieldControl(wx.Panel, wx.TextDropTarget):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, pos=(0,375), size=(700,300))
        self.SetDropTarget(FieldDropTarget(parent))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self._background = parent._engine.GetSkinImage('FieldPlayer')

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self._background, 0, 0)
    
class FieldDropTarget(wx.TextDropTarget):
    def __init__(self, game):
        wx.TextDropTarget.__init__(self)
        self._game = game
    
    def OnDropText(self, x, y, data):
        self._game.OnCardDropOnField(x, y, data)

class OpponentFieldControl(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, pos=(0,41), size=(700,300))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self._background = parent._engine.GetSkinImage('OpponentField')

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self._background, 0, 0)

class DeckListControl(wx.Frame):
    def __init__(self, parent):
        self._game = parent
        wx.Frame.__init__(self, parent, -1, 'Deck', pos=(400,300), size=(670,400), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self._game.OnPopupDeckSearch()

class OpponentDeckListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Opponent Deck', pos=(400,300), size=(670,400), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Hide()
        
class DeckListDropTarget(wx.TextDropTarget):
    def __init__(self, game):
        wx.TextDropTarget.__init__(self)
        self._game = game
    
    def OnDropText(self, x, y, data):
        self._game.OnCardDropOnDeck(x, y, data)
        pass

class OpponentGraveListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Opponent Graveyard', pos=(400,300), size=(670,400), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Parent.OnOpponentGraveLClick()

class GraveListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Graveyard', pos=(400,300), size=(670,400), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.SetDropTarget(GraveListDropTarget(parent))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Parent.OnGraveLClick()
        
class GraveListDropTarget(wx.TextDropTarget):
    def __init__(self, game):
        wx.TextDropTarget.__init__(self)
        self._game = game
    
    def OnDropText(self, x, y, data):
        self._game.OnCardDropOnGrave(x, y, data)

class Stack_1_ListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Stack 1', pos=(400,300), size=(202,270), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.SetDropTarget(Stack_1_ListDropTarget(parent))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Parent.OnStack_1_LClick()
        
class Stack_1_ListDropTarget(wx.TextDropTarget):
    def __init__(self, game):
        wx.TextDropTarget.__init__(self)
        self._game = game
    
    def OnDropText(self, x, y, data):
        self._game.OnCardDropOnStack1(x, y, data)

class Stack_2_ListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Stack 2', pos=(400,300), size=(202,270), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.SetDropTarget(Stack_2_ListDropTarget(parent))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Parent.OnStack_2_LClick()
        
class Stack_2_ListDropTarget(wx.TextDropTarget):
    def __init__(self, game):
        wx.TextDropTarget.__init__(self)
        self._game = game
    
    def OnDropText(self, x, y, data):
        self._game.OnCardDropOnStack2(x, y, data)
        

class Stack_3_ListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Stack 3', pos=(400,300), size=(202,270), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.SetDropTarget(Stack_3_ListDropTarget(parent))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Parent.OnStack_3_LClick()
        
class Stack_3_ListDropTarget(wx.TextDropTarget):
    def __init__(self, game):
        wx.TextDropTarget.__init__(self)
        self._game = game
    
    def OnDropText(self, x, y, data):
        self._game.OnCardDropOnStack3(x, y, data)

class Stack_4_ListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Stack 4', pos=(400,300), size=(202,270), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.SetDropTarget(Stack_4_ListDropTarget(parent))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Parent.OnStack_4_LClick()
        
class Stack_4_ListDropTarget(wx.TextDropTarget):
    def __init__(self, game):
        wx.TextDropTarget.__init__(self)
        self._game = game
    
    def OnDropText(self, x, y, data):
        self._game.OnCardDropOnStack4(x, y, data)
        
class Stack_5_ListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Stack 5', pos=(400,300), size=(202,270), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.SetDropTarget(Stack_5_ListDropTarget(parent))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Parent.OnStack_5_LClick()
        
class Stack_5_ListDropTarget(wx.TextDropTarget):
    def __init__(self, game):
        wx.TextDropTarget.__init__(self)
        self._game = game
    
    def OnDropText(self, x, y, data):
        self._game.OnCardDropOnStack5(x, y, data)

class OpponentRFGListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Opponent RFG', pos=(400,300), size=(670,400), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Parent.OnGamePopupOpponentRFG()

class OpponentFusionDeckListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Opponent's Extra-Deck", pos=(400,300), size=(670,400), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Hide()

class OpponentSideDeckListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Opponent's Side-Deck", pos=(400,300), size=(345,298), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Hide()

class FusionDeckListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Extra-Deck', pos=(400,300), size=(345,298), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.SetDropTarget(FusionDeckListDropTarget(parent))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Parent.OnGamePopupFusionDeck()

class SideDeckListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Side-Deck', pos=(400,300), size=(345,298), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.SetDropTarget(SideDeckListDropTarget(parent))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Parent.OnGamePopupSideDeck()

class FusionDeckListDropTarget(wx.TextDropTarget):
    def __init__(self, game):
        wx.TextDropTarget.__init__(self)
        self._game = game
    
    def OnDropText(self, x, y, data):
        self._game.OnCardDropOnFusionDeck(x, y, data)

class SideDeckListDropTarget(wx.TextDropTarget):
    def __init__(self, game):
        wx.TextDropTarget.__init__(self)
        self._game = game
    
    def OnDropText(self, x, y, data):
        self._game.OnCardDropOnSideDeck(x, y, data)

class RFGListControl(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'RFG', pos=(400,300), size=(670,400), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.SetDropTarget(RFGListDropTarget(parent))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Scroll = wx.ScrolledWindow(self,-1)
        self.Scroll.SetScrollbars(0, 1, 0, 200)
        self.Scroll.SetBackgroundColour(wx.Colour(33,35,36))

    def OnClose(self, event=None):
        self.Parent.OnGamePopupRFG()

class RFGListDropTarget(wx.TextDropTarget):
    def __init__(self, game):
        wx.TextDropTarget.__init__(self)
        self._game = game
    
    def OnDropText(self, x, y, data):
        self._game.OnCardDropOnRFG(x, y, data)

class DeckControl(GameObject):
    def __init__(self, parent, pos, t):
        GameObject.__init__(self, parent, pos, t)
    
class FusionDeckControl(GameObject):
    def __init__(self, parent, pos, t):
        GameObject.__init__(self, parent, pos, t)
    
class SideDeckControl(GameObject):
    def __init__(self, parent, pos, t):
        GameObject.__init__(self, parent, pos, t)

class OpponentDeckControl(GameObject):
    def __init__(self, parent, pos, t):
        GameObject.__init__(self, parent, pos, t)

class GraveControl(GameObject):
    def __init__(self, parent, pos, t, game):
        self._game = game
        GameObject.__init__(self, parent, pos, t)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        if len(self._game._grave) > 0:
            dc.DrawBitmap(self._game._engine.GetCardGraveImage(self._game._grave[0]), 1, 1, True)
        else:
            dc.SetBrush(wx.Brush(wx.Colour(33,35,36)))
            dc.SetPen(wx.Pen(wx.Colour(33,35,36)))
            dc.DrawRectangle(0,0,self._texture.GetWidth(), self._texture.GetHeight())
        dc.DrawBitmap(self._texture, 0, 0, True)

    def UpdateCardTooltip(self, l):
        d = 0
        s = 'Graveyard: ' + str(len(l))
        if len(l) > 10:
            l = l[:11]
            d = 1
        for c in l:
            s += '\n' + c.GetCardName()
        if d:
            s += '\n...'
        tip = wx.ToolTip(s)
        tip.SetDelay(250)
        self.SetToolTip(tip)
        self.Hide()
        self.Show()

class Stack_1_Control(GameObject):
    def __init__(self, parent, pos, t, game):
        self._game = game
        GameObject.__init__(self, parent, pos, t)

    def UpdateCardTooltip(self, l):
        d = 0
        s = 'Stack 1: ' + str(len(l))
        if len(l) > 10:
            l = l[:11]
            d = 1
        for c in l:
            s += '\n' + c.GetCardName()
        if d:
            s += '\n...'
        tip = wx.ToolTip(s)
        tip.SetDelay(250)
        self.SetToolTip(tip)
        self.Hide()
        self.Show()
   
class Stack_2_Control(GameObject):
    def __init__(self, parent, pos, t, game):
        self._game = game
        GameObject.__init__(self, parent, pos, t)

    def UpdateCardTooltip(self, l):
        d = 0
        s = 'Stack 2: ' + str(len(l))
        if len(l) > 10:
            l = l[:11]
            d = 1
        for c in l:
            s += '\n' + c.GetCardName()
        if d:
            s += '\n...'
        tip = wx.ToolTip(s)
        tip.SetDelay(250)
        self.SetToolTip(tip)
        self.Hide()
        self.Show()

class Stack_3_Control(GameObject):
    def __init__(self, parent, pos, t, game):
        self._game = game
        GameObject.__init__(self, parent, pos, t)

    def UpdateCardTooltip(self, l):
        d = 0
        s = 'Stack 3: ' + str(len(l))
        if len(l) > 10:
            l = l[:11]
            d = 1
        for c in l:
            s += '\n' + c.GetCardName()
        if d:
            s += '\n...'
        tip = wx.ToolTip(s)
        tip.SetDelay(250)
        self.SetToolTip(tip)
        self.Hide()
        self.Show()

class Stack_4_Control(GameObject):
    def __init__(self, parent, pos, t, game):
        self._game = game
        GameObject.__init__(self, parent, pos, t)

    def UpdateCardTooltip(self, l):
        d = 0
        s = 'Stack 4: ' + str(len(l))
        if len(l) > 10:
            l = l[:11]
            d = 1
        for c in l:
            s += '\n' + c.GetCardName()
        if d:
            s += '\n...'
        tip = wx.ToolTip(s)
        tip.SetDelay(250)
        self.SetToolTip(tip)
        self.Hide()
        self.Show()

class Stack_5_Control(GameObject):
    def __init__(self, parent, pos, t, game):
        self._game = game
        GameObject.__init__(self, parent, pos, t)

    def UpdateCardTooltip(self, l):
        d = 0
        s = 'Stack 5: ' + str(len(l))
        if len(l) > 10:
            l = l[:11]
            d = 1
        for c in l:
            s += '\n' + c.GetCardName()
        if d:
            s += '\n...'
        tip = wx.ToolTip(s)
        tip.SetDelay(250)
        self.SetToolTip(tip)
        self.Hide()
        self.Show()




class RFGControl(GameObject):
    def __init__(self, parent, pos, t, game):
        self._game = game
        GameObject.__init__(self, parent, pos, t)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        if len(self._game._rfg) > 0:
            dc.DrawBitmap(self._game._engine.GetCardGraveImage(self._game._rfg[0]), 1, 1, True)
        else:
            dc.SetBrush(wx.Brush(wx.Colour(33,35,36)))
            dc.SetPen(wx.Pen(wx.Colour(33,35,36)))
            dc.DrawRectangle(0,0,self._texture.GetWidth(), self._texture.GetHeight())
        dc.DrawBitmap(self._texture, 0, 0, True)

    def UpdateCardTooltip(self, l):
        d = 0
        s = 'RFG: ' + str(len(l))
        if len(l) > 10:
            l = l[:11]
            d = 1
        for c in l:
            s += '\n' + c.GetCardName()
        if d:
            s += '\n...'
        tip = wx.ToolTip(s)
        tip.SetDelay(250)
        self.SetToolTip(tip)
        self.Hide()
        self.Show()

class OpponentGraveControl(GameObject):
    def __init__(self, parent, pos, t, game):
        self._game = game
        GameObject.__init__(self, parent, pos, t)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        if len(self._game._opponentgrave) > 0:
            dc.DrawBitmap(self._game._engine.GetCardGraveImage(self._game._opponentgrave[0]), 0, 0, True)
        else:
            dc.SetBrush(wx.Brush(wx.Colour(33,35,36)))
            dc.SetPen(wx.Pen(wx.Colour(33,35,36)))
            dc.DrawRectangle(0,0,self._texture.GetWidth(), self._texture.GetHeight())
        dc.DrawBitmap(self._texture, 0, 0, True)

    def UpdateCardTooltip(self, l):
        d = 0
        s = 'Graveyard: ' + str(len(l))
        if len(l) > 10:
            l = l[:11]
            d = 1
        for c in l:
            s += '\n' + c.GetCardName()
        if d:
            s += '\n...'
        tip = wx.ToolTip(s)
        tip.SetDelay(250)
        self.SetToolTip(tip)
        self.Hide()
        self.Show()

class OpponentRFGControl(GameObject):
    def __init__(self, parent, pos, t, game):
        self._game = game
        GameObject.__init__(self, parent, pos, t)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        if len(self._game._opponentrfg) > 0:
            dc.DrawBitmap(self._game._engine.GetCardGraveImage(self._game._opponentrfg[0]), 0, 0, True)
        else:
            dc.SetBrush(wx.Brush(wx.Colour(33,35,36)))
            dc.SetPen(wx.Pen(wx.Colour(33,35,36)))
            dc.DrawRectangle(0,0,self._texture.GetWidth(), self._texture.GetHeight())
        dc.DrawBitmap(self._texture, 0, 0, True)

    def UpdateCardTooltip(self, l):
        d = 0
        s = 'RFG: ' + str(len(l))
        if len(l) > 10:
            l = l[:11]
            d = 1
        for c in l:
            s += '\n' + c.GetCardName()
        if d:
            s += '\n...'
        tip = wx.ToolTip(s)
        tip.SetDelay(250)
        self.SetToolTip(tip)
        self.Hide()
        self.Show()

class HandControl(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=(1,676), size=(698,100))
        self.SetBackgroundColour(wx.Colour(33,35,36))
        self.SetDropTarget(HandListDropTarget(parent))
        
'''class HandControl(wx.Frame):
    def __init__(self, parent):
        self._game = parent
        wx.Frame.__init__(self, parent, -1, 'Hand', pos=(1,676), size=(698,100), style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT)
        self.SetBackgroundColour(wx.Colour(33,35,36))
        self.SetDropTarget(HandListDropTarget(parent))'''

class HandListDropTarget(wx.TextDropTarget):
    def __init__(self, game):
        wx.TextDropTarget.__init__(self)
        self._game = game
    
    def OnDropText(self, x, y, data):
        self._game.OnCardDropOnHand(x, y, data)

class OpponentHandControl(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=(1,0), size=(698,40))
        self.SetBackgroundColour(wx.Colour(33,35,36))

class ScoreControl(GameObject):
    def __init__(self, parent):
        self._game = parent
        self._engine = self._game._engine
        GameObject.__init__(self, parent, (0,341), self._engine.GetSkinImage('Score'))
        self._player_score = 8000
        self._opponent_score = 8000
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        # Player
        self._player_menu = wx.Menu()
        item = wx.MenuItem(self._player_menu, -1, '-2000')
        self._player_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPlayerPopupSub2000, item)
        item = wx.MenuItem(self._player_menu, -1, '-1000')
        self._player_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPlayerPopupSub1000, item)
        item = wx.MenuItem(self._player_menu, -1, '-500')
        self._player_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPlayerPopupSub500, item)
        item = wx.MenuItem(self._player_menu, -1, '-200')
        self._player_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPlayerPopupSub200, item)
        item = wx.MenuItem(self._player_menu, -1, '-100')
        self._player_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPlayerPopupSub100, item)
        item = wx.MenuItem(self._player_menu, -1, '-50')
        self._player_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPlayerPopupSub50, item)
        item = wx.MenuItem(self._player_menu, -1, '-25')
        self._player_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPlayerPopupSub25, item)
        item = wx.MenuItem(self._player_menu, -1, '+1000')
        self._player_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPlayerPopupAdd1000, item)
        item = wx.MenuItem(self._player_menu, -1, '+500')
        self._player_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPlayerPopupAdd500, item)
        item = wx.MenuItem(self._player_menu, -1, '+100')
        self._player_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPlayerPopupAdd100, item)
        item = wx.MenuItem(self._player_menu, -1, '+50')
        self._player_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPlayerPopupAdd50, item)
        item = wx.MenuItem(self._player_menu, -1, '+25')
        self._player_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnPlayerPopupAdd25, item)
        # Opponent
        #self._opponent_menu = wx.Menu()
        #item = wx.MenuItem(self._opponent_menu, -1, '-2000')
        #self._opponent_menu.AppendItem(item)
        #self.Bind(wx.EVT_MENU, self.OnOpponentPopupSub2000, item)
        #item = wx.MenuItem(self._opponent_menu, -1, '-1000')
        #self._opponent_menu.AppendItem(item)
        #self.Bind(wx.EVT_MENU, self.OnOpponentPopupSub1000, item)
        #item = wx.MenuItem(self._opponent_menu, -1, '-500')
        #self._opponent_menu.AppendItem(item)
        #self.Bind(wx.EVT_MENU, self.OnOpponentPopupSub500, item)
        #item = wx.MenuItem(self._opponent_menu, -1, '-200')
        #self._opponent_menu.AppendItem(item)
        #self.Bind(wx.EVT_MENU, self.OnOpponentPopupSub200, item)
        #item = wx.MenuItem(self._opponent_menu, -1, '-100')
        #self._opponent_menu.AppendItem(item)
        #self.Bind(wx.EVT_MENU, self.OnOpponentPopupSub100, item)
        #item = wx.MenuItem(self._opponent_menu, -1, '-50')
        #self._opponent_menu.AppendItem(item)
        #self.Bind(wx.EVT_MENU, self.OnOpponentPopupSub50, item)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self._texture, 0, 0, True)
        
        font = wx.Font(pointSize=9,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL, faceName="Tahoma")
        font.SetNoAntiAliasing(True)
        dc.SetFont(font)
        dc.SetTextForeground(wx.WHITE)
        dc.DrawText(str(self._player_score), 16, 10)
        dc.DrawText(str(self._opponent_score), 82, 10)

    def OnRightUp(self, event):
        if self._game.Hit(event.GetX(), event.GetY(), wx.Rect(1,1,62,32)):
            self.OnPlayerPopup()
        #elif self._game.Hit(event.GetX(), event.GetY(), wx.Rect(64,1,64,32)):
            #self.OnOpponentPopup()

    def OnPlayerPopup(self):
        self.PopupMenu(self._player_menu)
    
    def OnPlayerPopupSub2000(self, event):
        self.SetPlayerScoreDiff(-2000)

    def OnPlayerPopupSub1000(self, event):
        self.SetPlayerScoreDiff(-1000)

    def OnPlayerPopupSub500(self, event):
        self.SetPlayerScoreDiff(-500)

    def OnPlayerPopupSub200(self, event):
        self.SetPlayerScoreDiff(-200)

    def OnPlayerPopupSub100(self, event):
        self.SetPlayerScoreDiff(-100)

    def OnPlayerPopupSub50(self, event):
        self.SetPlayerScoreDiff(-50)

    def OnPlayerPopupSub25(self, event):
        self.SetPlayerScoreDiff(-25)

    def OnPlayerPopupAdd1000(self, event):
        self.SetPlayerScoreDiff(1000)

    def OnPlayerPopupAdd500(self, event):
        self.SetPlayerScoreDiff(500)

    def OnPlayerPopupAdd100(self, event):
        self.SetPlayerScoreDiff(100)

    def OnPlayerPopupAdd50(self, event):
        self.SetPlayerScoreDiff(50)

    def OnPlayerPopupAdd25(self, event):
        self.SetPlayerScoreDiff(25)

    def OnOpponentPopup(self):
        self.PopupMenu(self._opponent_menu)

    def OnOpponentPopupSub2000(self, event):
        self.SetOpponentScoreDiff(-2000)

    def OnOpponentPopupSub1000(self, event):
        self.SetOpponentScoreDiff(-1000)

    def OnOpponentPopupSub500(self, event):
        self.SetOpponentScoreDiff(-500)

    def OnOpponentPopupSub200(self, event):
        self.SetOpponentScoreDiff(-200)

    def OnOpponentPopupSub100(self, event):
        self.SetOpponentScoreDiff(-100)

    def OnOpponentPopupSub50(self, event):
        self.SetOpponentScoreDiff(-50)

    def SetPlayerScoreDiff(self, diff):
        self._game.WriteLifeChangePacket(diff)
        self._player_score += diff
        if diff > 0:
            self._game.WriteGameMessage(self._engine.GetLangString("gains ") + str(abs(diff)) + " life points (" + str(self._player_score) + ")" , CHAT_PLAYER)
        else:
            self._game.WriteGameMessage(self._engine.GetLangString("loses ") + str(abs(diff)) + " life points (" + str(self._player_score) + ")" , CHAT_PLAYER)
        self.Hide()
        self.Show()

    def SetOpponentScoreDiff(self, diff):
        self._opponent_score += diff
        if diff > 0:
            self._game.WriteGameMessage(self._engine.GetLangString("gains ") + str(abs(diff)) + " life points (" + str(self._opponent_score) + ")" , CHAT_OPPONENT)
        else:
            self._game.WriteGameMessage(self._engine.GetLangString("loses ") + str(abs(diff)) + " life points (" + str(self._opponent_score) + ")" , CHAT_OPPONENT)
        self.Hide()
        self.Show()

    def SetPlayerScore(self, score):
        self._player_score = score
        self._game.WriteGameMessage(self._engine.GetLangString("'s life points is now ") + str(self._player_score) , CHAT_PLAYER)
        self.Hide()
        self.Show()

    def SetOpponentScore(self, score):
        self._opponent_score = score
        self._game.WriteGameMessage(self._engine.GetLangString("'s life points is now ") + str(self._opponent_score) , CHAT_OPPONENT)
        self.Hide()
        self.Show()

class CardControl(GameObject, wx.DataObjectSimple):
    def __init__(self, parent, card, engine, game, serial, cpos=0, cardmode=0, cardface=1):
        self._card = card
        self._cardposition = cpos
        self._cardface = cardface
        self._cardmode = cardmode
        self._engine = engine
        self._game = game
        self._cardtarget = False
        self._counters = 0
        t = self._engine.GetCardImage(self)
        GameObject.__init__(self, parent, (0,0), t)
        wx.DataObjectSimple.__init__(self)
        self.Bind(wx.EVT_MOTION, self.OnDrag)
        self._serial = serial
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWell)

    def AddCounters(self, n=1):
        self._counters += n
        self.Hide()
        self.Show()

    def RemoveCounters(self, n=1):
        self._counters -= n
        if self._counters < 0:
            self._counters = 0
        self.Hide()
        self.Show()

    def OnMouseWell(self, event):
        self._game._carddescriptionctrl.ScrollLines(-event.GetWheelRotation())

    def Target(self):
        if self._cardtarget:
            self._cardtarget = False
        else:
            self._cardtarget = True

    def IsTarget(self):
        return self._cardtarget

    def OnRightUp(self, event):
        self._game.OnCardPopup(self)
    
    def OnMouseOver(self, event):
        type2=''
        desc = self._card.Type + '\n'
        if len(self._card.Type2) > 0:
            desc += self._card.Type2 + '\n'
            type2 = self._card.Type2
        desc += '\n' + self._card.Effect
        attrib = self._card.Attribute
        stars = self._card.Stars + '*'
        typecf=''
        typec = re.search('Tuner', self._card.Type)
        typeE = re.search('Exceed', self._card.Type)
        if typec:
            typecf = typec.group ( 0 )
        if typeE:
            typecf = typeE.group ( 0 )
        typecm= ''
        if attrib != 'Spell' or attrib!= 'Trap':
            string = "/"
            typecm = ''
            f = self._card.Type
            for character in f:
                if character.find(string) == -1:
                    typecm=typecm+character
                else:
                    break
        self._game.RefreshCardInfo(self._card.Name, self._engine.GetBigCardImage(self._card), desc, attrib, type2, stars, typecf, typecm)
    
    def RefreshTexture(self):
        self._texture = self._engine.GetCardImage(self)
        self.SetSize((self._texture.GetWidth(), self._texture.GetHeight()))

    def OnDrag(self, event):
        if not event.Dragging():
            return
        if not event.LeftIsDown():
            return
        tt = self.GetSerial()
        tdo = wx.TextDataObject(tt)
        tds = wx.DropSource(self)
        tds.SetData(tdo)
        tds.DoDragDrop(True)
    
    def GetCardName(self):
        return self._card.Name
    
    '''def GetCardStats(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap':
            return self._card.Atk + '/' + self._card.Def
        else:
            return self._card.Atk + ' ' + self._card.Def'''
    
    def GetCardEffect(self):
        return self._card.Effect
    
    def GetCardAttribute(self):
        return self._card.Attribute
    
    def GetCardType(self):
        return self._card.Type
    
    def GetCardPosition(self):
        return self._cardposition
    
    def GetCardFace(self):
        return self._cardface
    
    def GetCardMode(self):
        return self._cardmode

    def GetSerial(self):
        return self._serial

    def IsMonster(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap':
            return True
        else:
            return False

    def IsNormalMonster(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap' and self._card.Type.count('Effect') == 0: return True
        else: return False

    def IsEffectMonster(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap' and self._card.Type.count('Effect') > 0: return True
        else: return False

    def IsFusion(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap' and self._card.Type.count('Fusion') > 0 or self._card.Type.count('Exceed') > 0:
            return True
        else:
            return False

    def IsSynchro(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap' and self._card.Type.count('Synchro') > 0:
            return True
        else:
            return False
    
    def IsToken(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap' and self._card.Type.count('Token') > 0:
            return True
        else:
            return False

    def IsRitual(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap' and self._card.Type.count('Ritual') > 0: return True
        else: return False

    def IsTrap(self):
        if self._card.Attribute == 'Trap': return True
        else: return False

    def IsSpell(self):
        if self._card.Attribute == 'Spell': return True
        else: return False

    def IsFaceDown(self):
        if self._cardface == FACE_DOWN:
            return 1
        else:
            return 0

    def IsFaceUp(self):
        if self._cardface == FACE_UP:
            return 1
        else:
            return 0

    def IsHorizontal(self):
        if self._cardmode == CARD_HORIZONTAL:
            return 1
        else:
            return 0

    def IsVertical(self):
        if self._cardmode == CARD_VERTICAL:
            return 1
        else:
            return 0

    def SetCardPosition(self, p):
        if self.IsTarget():
            self.Target()
        self._cardposition = p

    def SetCardState(self, pos=POS_FIELD, mode=CARD_VERTICAL, face=FACE_UP):
        self._cardposition = pos
        self._cardmode = mode
        self._cardface = face
        if self.IsTarget():
            self.Target()
        if not pos == POS_FIELD:
            self.RemoveCounters(self._counters)
        self.RefreshTexture()

    def FaceUp(self):
        if self.IsTarget():
            self.Target()
        self._cardface = FACE_UP

    def FaceDown(self):
        if self.IsTarget():
            self.Target()
        self._cardface = FACE_DOWN

    def Vertical(self):
        if self.IsTarget():
            self.Target()
        self._cardmode = CARD_VERTICAL

    def Horizontal(self):
        if self.IsTarget():
            self.Target()
        self._cardmode = CARD_HORIZONTAL

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self._texture, 0, 0, True)
        font = wx.Font(pointSize=8,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL, faceName="Tahoma")
        font.SetNoAntiAliasing(True)
        dc.SetFont(font)
        name = self.GetCardName()
        p = self.GetCardPosition()
        if p == 2 or p == 3 or p == 4 or p == 5 or p == 6:
            name = name[:26]
            nx = 2
            ny = 1
            sx = 10
            sy = 10
            '''dc.SetTextForeground(wx.BLACK)
            dc.DrawText(name, nx, ny)'''
        if self.IsTarget():
            tbmp = self._engine.GetSkinImage('Target')
            if self.IsVertical():
                dc.DrawBitmap(tbmp, 14, 24, True)
            else:
                dc.DrawBitmap(tbmp, 28, 18, True)
        if self._counters > 0:
            dc.SetTextForeground('#000000')
            dc.SetFont(wx.Font(pointSize=10,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_BOLD, faceName="Tahoma"))
            if self.IsVertical():
                dc.GradientFillLinear((8, 55, 14, 14), '#ffffff', '#ffffff', wx.NORTH)
                dc.DrawText(str(self._counters), 8, 55)
            else:
                dc.GradientFillLinear((8, 28, 14, 14), '#ffffff', '#ffffff', wx.NORTH)
                dc.DrawText(str(self._counters), 8, 28)

class OpponentCardControl(GameObject):
    def __init__(self, parent, card, engine, game, serial, cpos=0, cardmode=0, cardface=1):
        self._card = card
        self._cardposition = cpos
        self._cardface = cardface
        self._cardmode = cardmode
        self._engine = engine
        self._game = game
        self._counters = 0
        self._cardtarget = False
        t = self._engine.GetCardImage(self)
        GameObject.__init__(self, parent, (0,0), t)
        self._serial = serial
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWell)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

    def AddCounters(self, n=1):
        self._counters += n
        self.Hide()
        self.Show()

    def RemoveCounters(self, n=1):
        self._counters -= n
        if self._counters < 0:
            self._counters = 0
        self.Hide()
        self.Show()

    def OnMouseWell(self, event):
        if self.IsFaceUp():
            self._game._carddescriptionctrl.ScrollLines(-event.GetWheelRotation())

    def Target(self):
        if self._cardtarget:
            self._cardtarget = False
        else:
            self._cardtarget = True

    def IsTarget(self):
        return self._cardtarget

    def OnRightUp(self, event):
        self._game._opponentcurrentcard = self
        self._game.OnOpponentCardTarget()
    
    def OnMouseOver(self, event):
        if self.IsFaceDown():
            return
        type2=''
        desc = self._card.Type + '\n'
        if len(self._card.Type2) > 0:
            desc += self._card.Type2 + '\n'
            type2 = self._card.Type2
        desc += '\n' + self._card.Effect
        attrib = self._card.Attribute
        stars = self._card.Stars + '*'
        typecf=''
        typec = re.search('Tuner', self._card.Type)
        typeE = re.search('Exceed', self._card.Type)
        if typec:
            typecf = typec.group ( 0 )
        if typeE:
            typecf = typeE.group ( 0 )
        typecm= ''
        if attrib != 'Spell' or attrib!= 'Trap':
            string = "/"
            typecm = ''
            f = self._card.Type
            for character in f:
                if character.find(string) == -1:
                    typecm=typecm+character
                else:
                    break
        self._game.RefreshCardInfo(self._card.Name, self._engine.GetBigCardImage(self._card), desc, attrib, type2, stars, typecf, typecm)
    
    def RefreshTexture(self):
        self._texture = self._engine.GetCardImage(self)
        self.SetSize((self._texture.GetWidth(), self._texture.GetHeight()))
    
    def GetCardName(self):
        return self._card.Name
    
    def GetCardStats(self):
        return self._card.Atk + '/' + self._card.Def
    
    def GetCardEffect(self):
        return self._card.Effect
    
    def GetCardAttribute(self):
        return self._card.Attribute
    
    def GetCardType(self):
        return self._card.Type
    
    def GetCardPosition(self):
        return self._cardposition
    
    def GetCardFace(self):
        return self._cardface
    
    def GetCardMode(self):
        return self._cardmode

    def GetSerial(self):
        return self._serial

    def IsMonster(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap': return True
        else: return False

    def IsNormalMonster(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap' and self._card.Type.count('Effect') == 0: return True
        else: return False

    def IsEffectMonster(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap' and self._card.Type.count('Effect') > 0: return True
        else: return False

    def IsFusion(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap' and self._card.Type.count('Fusion') > 0 or self._card.Type.count('Exceed') > 0: return True
        else: return False
    
    def IsSynchro(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap' and self._card.Type.count('Synchro') > 0: return True
        else: return False
    
    def IsToken(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap' and self._card.Type.count('Token') > 0: return True
        else: return False

    def IsRitual(self):
        if self._card.Attribute != 'Spell' and self._card.Attribute != 'Trap' and self._card.Type.count('Ritual') > 0: return True
        else: return False

    def IsTrap(self):
        if self._card.Attribute == 'Trap': return True
        else: return False

    def IsSpell(self):
        if self._card.Attribute == 'Spell': return True
        else: return False

    def IsFaceDown(self):
        if self._cardface == FACE_DOWN:
            return 1
        else:
            return 0

    def IsFaceUp(self):
        if self._cardface == FACE_UP:
            return 1
        else:
            return 0

    def IsHorizontal(self):
        if self._cardmode == CARD_HORIZONTAL:
            return 1
        else:
            return 0

    def IsVertical(self):
        if self._cardmode == CARD_VERTICAL:
            return 1
        else:
            return 0

    def SetCardPosition(self, p):
        if self.IsTarget():
            self.Target()
        self._cardposition = p

    def SetCardState(self, pos=POS_OPP_FIELD, mode=CARD_VERTICAL, face=FACE_UP):
        self._cardposition = pos
        self._cardmode = mode
        self._cardface = face
        if self.IsTarget():
            self.Target()
        if not pos == POS_FIELD:
            self.RemoveCounters(self._counters)
        self.RefreshTexture()

    def FaceUp(self):
        if self.IsTarget():
            self.Target()
        self._cardface = FACE_UP

    def FaceDown(self):
        if self.IsTarget():
            self.Target()
        self._cardface = FACE_DOWN

    def Vertical(self):
        if self.IsTarget():
            self.Target()
        self._cardmode = CARD_VERTICAL

    def Horizontal(self):
        if self.IsTarget():
            self.Target()
        self._cardmode = CARD_HORIZONTAL

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self._texture, 0, 0, True)
        font = wx.Font(pointSize=8,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL, faceName="Tahoma")
        font.SetNoAntiAliasing(True)
        dc.SetFont(font)
        name = self.GetCardName()
        p = self.GetCardPosition()
        if p == 9 or p == 10 or p == 11 or p == 12 or p == 13:
            name = name[:26]
            nx = 2
            ny = 1
            sx = 10
            sy = 10
            dc.SetTextForeground(wx.BLACK)
            dc.DrawText(name, nx, ny)
        if self.IsTarget():
            tbmp = self._engine.GetSkinImage('Target')
            if self.IsVertical():
                dc.DrawBitmap(tbmp, 14, 24, True)
            else:
                dc.DrawBitmap(tbmp, 28, 18, True)
        if self._counters > 0:
            if self.IsFaceDown():
                dc.SetTextForeground(wx.WHITE)
            else:
                dc.SetTextForeground(wx.BLACK)
            dc.SetFont(wx.Font(pointSize=9,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_BOLD, faceName="Tahoma"))
            if self.IsVertical():
                dc.DrawText(str(self._counters), 8, 48)
            else:
                dc.DrawText(str(self._counters), 7, 22)
    
class Note(GameObject):
    def __init__(self, parent, pos, game):
        self._game = game
        self._label = ""
        GameObject.__init__(self, parent, pos, self._game._engine.GetSkinImage('Note'))
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDClick)
        self.OnDClick()

    def OnRightUp(self, event=None):
        menu = wx.Menu()
        item = wx.MenuItem(menu, -1, "Delete")
        self.Bind(wx.EVT_MENU, self.OnDelete)
        menu.AppendItem(item)
        self.PopupMenu(menu)

    def OnDelete(self, event=None):
        self.Hide()
        self.Close()

    def OnDClick(self, event=None):
        dialog = wx.TextEntryDialog(self, "Insert the note's text")
        if dialog.ShowModal() == wx.ID_OK:
            self._label = dialog.GetValue()
            tip = wx.ToolTip(self._label)
            tip.SetDelay(250)
            self.SetToolTip(tip)
            self.Hide()
            self.Show()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self._texture, 0, 0, True)
        dc.SetFont(wx.Font(pointSize=7,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL, faceName="Verdana"))
        dc.SetTextForeground(wx.BLACK)
        l = len(self._label)
        if l > 10:
            line1 = self._label[:11]
            dc.DrawText(line1, 2, 2)
            if l > 20:
                line2 = self._label[10:21]
                dc.DrawText(line2, 2, 15)
            else:
                line2 = self._label[11:len(self._label)]
                dc.DrawText(line2, 2, 15)
        else:
            dc.DrawText(self._label, 2, 2)

class DrawPhaseControl(GameObject):
    def __init__(self, parent):
        self._game = parent
        GameObject.__init__(self, parent, (241+80,341), self._game._engine.GetSkinImage('PhaseBack'))
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self._sel = False
        self._opp = False

    def SelectPhase(self):
        self._game.ClearPhases()
        self._sel = True
        self._opp = True
        self.Hide()
        self.Show()

    def IsSelected(self):
        return self._sel

    def OnLeftUp(self, event=None):
        self._game.WritePhasePacket(0)
        self._game.ClearPhases()
        self._sel = True
        self._opp = False
        self.Hide()
        self.Show()
        self._game.WriteGameMessage(self._game._engine.GetLangString('entered his Draw Phase'), CHAT_PLAYER)
        #self._game.OnDeckDraw()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self._texture, 0, 0, True)
        dc.SetFont(wx.Font(pointSize=9,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL, faceName="Tahoma"))
        if self._sel:
            if self._opp:
                dc.SetTextForeground(wx.RED)
            else:
                dc.SetTextForeground(wx.BLUE)
        else:
            dc.SetTextForeground(wx.WHITE)
        dc.DrawBitmap(self._texture, 0, 0, True)
        dc.DrawText("Draw", 18, 10)

class StandbyPhaseControl(GameObject):
    def __init__(self, parent):
        self._game = parent
        GameObject.__init__(self, parent, (304+80,341), self._game._engine.GetSkinImage('PhaseBack'))
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self._sel = False
        self._opp = False

    def SelectPhase(self):
        self._game.ClearPhases()
        self._sel = True
        self._opp = True
        self.Hide()
        self.Show()

    def IsSelected(self):
        return self._sel

    def OnLeftUp(self, event=None):
        self._game.WritePhasePacket(1)
        self._game.ClearPhases()
        self._sel = True
        self._opp = False
        self.Hide()
        self.Show()
        self._game.WriteGameMessage(self._game._engine.GetLangString('entered his Standby Phase'), CHAT_PLAYER)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self._texture, 0, 0, True)
        dc.SetFont(wx.Font(pointSize=9,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL, faceName="Tahoma"))
        if self._sel:
            if self._opp:
                dc.SetTextForeground(wx.RED)
            else:
                dc.SetTextForeground(wx.BLUE)
        else:
            dc.SetTextForeground(wx.WHITE)
        dc.DrawBitmap(self._texture, 0, 0, True)
        dc.DrawText("Standby", 10, 10)

class MainPhase1Control(GameObject):
    def __init__(self, parent):
        self._game = parent
        GameObject.__init__(self, parent, (367+80,341), self._game._engine.GetSkinImage('PhaseBack'))
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self._sel = False
        self._opp = False

    def SelectPhase(self):
        self._game.ClearPhases()
        self._sel = True
        self._opp = True
        self.Hide()
        self.Show()

    def IsSelected(self):
        return self._sel

    def OnLeftUp(self, event=None):
        self._game.WritePhasePacket(2)
        self._game.ClearPhases()
        self._sel = True
        self._opp = False
        self.Hide()
        self.Show()
        self._game.WriteGameMessage(self._game._engine.GetLangString('entered his Main Phase 1'), CHAT_PLAYER)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self._texture, 0, 0, True)
        dc.SetFont(wx.Font(pointSize=9,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL, faceName="Tahoma"))
        if self._sel:
            if self._opp:
                dc.SetTextForeground(wx.RED)
            else:
                dc.SetTextForeground(wx.BLUE)
        else:
            dc.SetTextForeground(wx.WHITE)
        dc.DrawBitmap(self._texture, 0, 0, True)
        dc.DrawText("Main 1", 14, 10)

class BattlePhaseControl(GameObject):
    def __init__(self, parent):
        self._game = parent
        GameObject.__init__(self, parent, (430+80,341), self._game._engine.GetSkinImage('PhaseBack'))
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self._sel = False
        self._opp = False

    def SelectPhase(self):
        self._game.ClearPhases()
        self._sel = True
        self._opp = True
        self.Hide()
        self.Show()

    def IsSelected(self):
        return self._sel

    def OnLeftUp(self, event=None):
        self._game.WritePhasePacket(3)
        self._game.ClearPhases()
        self._sel = True
        self._opp = False
        self.Hide()
        self.Show()
        self._game.WriteGameMessage(self._game._engine.GetLangString('entered his Battle Phase'), CHAT_PLAYER)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self._texture, 0, 0, True)
        dc.SetFont(wx.Font(pointSize=9,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL, faceName="Tahoma"))
        if self._sel:
            if self._opp:
                dc.SetTextForeground(wx.RED)
            else:
                dc.SetTextForeground(wx.BLUE)
        else:
            dc.SetTextForeground(wx.WHITE)
        dc.DrawBitmap(self._texture, 0, 0, True)
        dc.DrawText("Battle", 16, 10)

class MainPhase2Control(GameObject):
    def __init__(self, parent):
        self._game = parent
        GameObject.__init__(self, parent, (493+80,341), self._game._engine.GetSkinImage('PhaseBack'))
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self._sel = False
        self._opp = False

    def SelectPhase(self):
        self._game.ClearPhases()
        self._sel = True
        self._opp = True
        self.Hide()
        self.Show()

    def IsSelected(self):
        return self._sel

    def OnLeftUp(self, event=None):
        self._game.WritePhasePacket(4)
        self._game.ClearPhases()
        self._sel = True
        self._opp = False
        self.Hide()
        self.Show()
        self._game.WriteGameMessage(self._game._engine.GetLangString('entered his Main Phase 2'), CHAT_PLAYER)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self._texture, 0, 0, True)
        dc.SetFont(wx.Font(pointSize=9,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL, faceName="Tahoma"))
        if self._sel:
            if self._opp:
                dc.SetTextForeground(wx.RED)
            else:
                dc.SetTextForeground(wx.BLUE)
        else:
            dc.SetTextForeground(wx.WHITE)
        dc.DrawBitmap(self._texture, 0, 0, True)
        dc.DrawText("Main 2", 14, 10)

class EndPhaseControl(GameObject):
    def __init__(self, parent):
        self._game = parent
        GameObject.__init__(self, parent, (556+80,341), self._game._engine.GetSkinImage('PhaseBack'))
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self._sel = False
        self._opp = False

    def SelectPhase(self):
        self._game.ClearPhases()
        self._sel = True
        self._opp = True
        self.Hide()
        self.Show()

    def IsSelected(self):
        return self._sel

    def OnLeftUp(self, event=None):
        self._game.WritePhasePacket(5)
        self._game.ClearPhases()
        self._sel = True
        self._opp = False
        self.Hide()
        self.Show()
        self._game.WriteGameMessage(self._game._engine.GetLangString('end his turn.'), CHAT_PLAYER)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self._texture, 0, 0, True)
        dc.SetFont(wx.Font(pointSize=9,family=wx.FONTFAMILY_DEFAULT,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL, faceName="Tahoma"))
        if self._sel:
            if self._opp:
                dc.SetTextForeground(wx.RED)
            else:
                dc.SetTextForeground(wx.BLUE)
        else:
            dc.SetTextForeground(wx.WHITE)
        dc.DrawBitmap(self._texture, 0, 0, True)
        dc.DrawText("End", 20, 10)
        